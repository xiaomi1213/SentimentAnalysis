# coding: utf-8

"""
从句子中抽取top 5 aspects，使用训练好的fastText模型进行每个aspects的情感分类，
并汇总成summary。
"""

import json
import os
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk import RegexpParser

from utils import split_sentence,add_to_dict_list,Item,get_top_k,get_top_k_from_list,contains_related_aspect
from trainModel import SentimentModel

class Sentence(object):
    """
    extract aspects from sentence
    """

    # 与词干提取词形还原（stemming）很相似
    LEMMATIZER = WordNetLemmatizer()

    def __init__(self, origin_sentence: str):
        self.sentence = origin_sentence
        self.word_tokens = list()
        self.pos_tags = list()

    def word_tokenize(self):
        assert len(self.sentence) != 0
        self.word_tokens = word_tokenize(self.sentence)
        return self

    def pos_tag(self):
        assert len(self.word_tokens) != 0
        self.pos_tags = pos_tag(self.word_tokens)
        return self

    def lemmatize(self):
        assert len(self.word_tokens) != 0
        # 目前只针对名词，因为目标是提取名词短语
        self.word_tokens = [Sentence.LEMMATIZER.lemmatize(word) for word in self.word_tokens]
        return self

    def _noun_phrase(self):
        assert len(self.pos_tags) != 0
        grammar = ('''
               NP: {<DT|PP\$>?<JJ><NN>}     # chunk determiner/possessive, adjectives and noun 限定词/所有词，形容词和名词
              {<NNP>+}                      # chunk sequences of proper nouns 专有名词序列
              {<NN>+}                       # chunk consecutive nouns 连续名词
              ''')

        # 编译正则表达式的接口
        cp = RegexpParser(grammar)
        sentenceTree = cp.parse(self.pos_tags)
        nounPhrases = self._extract_np(sentenceTree)  # collect Noun Phrase
        return nounPhrases

    def _extract_np(self, psent):
        for subtree in psent.subtrees():
            if subtree.label() == 'NP':
                yield ' '.join(word for word, tag in subtree.leaves())

    def contain_aspect(self):
        aspects = list()
        for aspect in self._noun_phrase():
            aspects.append(aspect)
        return aspects


def extract_sentence_aspects(sentence: str):
    """
    从句子中获取相关的aspect
    :param sentence:
    :return:
    """
    sen = Sentence(sentence)
    return sen.word_tokenize().lemmatize().pos_tag().contain_aspect()


class SentenceItem(Item):
    """
    存储句子文本
    是否是消极状态
    情绪的score
    """

    def __init__(self, content, isNeg, score):
        super().__init__(score, content)
        self.content = content
        self.isNeg = isNeg


class Business(object):
    """
    针对某一个特定的bussiness:
    1. 获取其中TOP 5的评价aspect
    2. 针对特定的aspect提取出TOP 5评论
    """

    BUSINESS_PATH = r"..\data\split_data"
    FILE_SUFFIX = '.txt'

    # 把已经训练好的模型存放在文件里，并导入进来
    SENTIMENT_MODEL = SentimentModel()

    def __init__(self, business_id, business_name='default'):
        # 初始化变量以及函数
        self.business_id = business_id
        self.business_name = business_name
        self.aspects = list()
        self.aspects_reviews_neg = dict()
        self.aspects_reviews_pos = dict()
        self.business_path = os.path.join(Business.BUSINESS_PATH,(business_id+Business.FILE_SUFFIX))

        self.business_score = 0
        self.avg_score = 0.0

    def extract_aspects(self):
        """
        从一个business的review中抽取aspects
        """
        b_score = 0
        review_len = 0
        # 统计所有名词短语出现的次数
        all_aspects = dict()
        with open(self.business_path, 'r') as review_f:
            for line in review_f:
                if len(line) == 0:
                    continue

                review = json.loads(line.strip())
                review_len = review_len + 1
                b_score = b_score + review['stars']
                # 抽取文本里面的名词短语
                sentence_aspects = extract_sentence_aspects(review['text'])
                for aspect in sentence_aspects:
                    if aspect in all_aspects:
                        all_aspects[aspect] = all_aspects[aspect] + 1
                    else:
                        all_aspects[aspect] = 1

        # 取出TOP5
        list = get_top_k(all_aspects, 5)
        self.avg_score = b_score / review_len
        for word in list:
            self.aspects.append(word.content)
        return self

    def aspect_based_summary(self):
        """
        返回一个business的summary. 针对于每一个aspect计算出它的正面负面情感以及TOP reviews.
        具体细节请看给定的文档。
        """
        with open(self.business_path, 'r') as review_f:
            while True:
                line = review_f.readline()
                if len(line) == 0:
                    break
                review = json.loads(line)
                self._split_sentence_based_aspect(review['text'])

        summary = dict()
        for aspect in self.aspects:
            summary[aspect] = self._get_aspect_summary(aspect)

        return {'business_id': self.business_id,
                'business_name': self.business_name,
                'business_rating': self.avg_score,
                'aspect_summary': summary
                }

    def _split_sentence_based_aspect(self, text: str):
        """
        1. 分割review，
        2. 并判断是否包含某个aspect，判断是否包含某个特定aspect
        3. 如果包含则归到某个aspect下
        4. 预测其情感，归类到pos或者neg中
        :param sentence:
        :return:
        """
        sentences = split_sentence(text)
        for sentence in sentences:
            for aspect in self.aspects:
                if not contains_related_aspect(aspect, sentence):
                    continue
                # 如果包含相关的aspect，就进行情感预测
                preview = self._preview_sentiment(sentence)
                item = SentenceItem(sentence, preview['isNeg'], preview['score'])

                if preview['isNeg']:
                    add_to_dict_list(self.aspects_reviews_neg, aspect, item)
                else:
                    add_to_dict_list(self.aspects_reviews_pos, aspect, item)


    def _get_aspect_summary(self, aspect: str):
        """
        获取相关aspect 的相关评论
        :param aspect:
        :return:
        """
        result = dict()
        try:
            neg_list = get_top_k_from_list(self.aspects_reviews_neg[aspect], 5)
            result['neg'] = self._get_review_text(neg_list)
            pos_list = get_top_k_from_list(self.aspects_reviews_pos[aspect], 5)
            result['pos'] = self._get_review_text(pos_list)
        except:
            pass

        return result

    def _get_review_text(self, sentence_item_list):
        reviews = []
        for sentence_item in sentence_item_list:
            reviews.append(sentence_item.content)

        return reviews

    def _preview_sentiment(self, sentence: str):
        """
        预测句子包含的情感
        :param sentence:
        :return:
        """
        result = Business.SENTIMENT_MODEL.preview(sentence)
        return result


if __name__ == "__main__":
    # sentence = Sentence('Steve Jobs was the CEO of Apple Corp.')
    # print(sentence.word_tokenize().lemmatize().pos_tag().contain_aspect())

    ids = "TJgYiMxiQXmtcbvxFMWZNQ"
    business = Business(ids, 'jejad')
    business.extract_aspects().aspect_based_summary()
