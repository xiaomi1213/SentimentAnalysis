# coding: utf-8

"""
建立模型训练和测试数据并训练FasText模型进行情感分类。
"""

import json
import fasttext


def build_model_data():
    """
    建立模型训练和测试数据
    每条数据前面添加'__label__' 如果当前数据为1
    :return:
    """
    review_data = r"..\data\review.json"
    model_train_data = r"..\data\model_train.txt"
    label = '__label__'
    with open(review_data, 'r', encoding="utf8") as review_f, open(model_train_data, 'w', encoding="utf8") as train_f:
        for line in review_f:
            if len(line) == 0:
                continue
            review = json.loads(line.strip())
            sentence = ''
            if review['stars'] >= 4:
                text = review['text']
                text = text.replace('\n', '')
                sentence = label + str(1) + ' ' + text + '\n'
            elif review['stars'] <= 2:
                text = review['text']
                text = text.replace('\n', '')
                sentence = label + str(0) + ' ' + text + '\n'
            if not (len(sentence) == 0 & sentence.isspace()):
                train_f.write(sentence)


FAST_TEXT_TEST_DATA = r"..\data\data_test.txt"
FAST_TEXT_TRAIN_DATA = r"..\data\data_train.txt"
def train_test_split():
    with open(r"..\data\model_train.txt", "r", encoding="utf8") as f:
        index = 0
        train = open(FAST_TEXT_TRAIN_DATA, "w", encoding="utf8")
        test = open(FAST_TEXT_TEST_DATA, "w", encoding="utf8")
        for line in f:
            index = index + 1
            if index < 50000:
                test.write(line)
            else:
                train.write(line)
        train.close()
        test.close()


FAST_TEXT_MODEL = r"..\data\fast_text.bin"
class FastText(object):
    def __init__(self):
        pass

    def train(self):
        model = fasttext.train_supervised(input=FAST_TEXT_TRAIN_DATA, lr=1.0, epoch=25, wordNgrams=2, bucket=200000,
                                          dim=50, loss='hs')
        model.save_model(FAST_TEXT_MODEL)
        print(model.test(FAST_TEXT_TEST_DATA, k=-1))

    def preview(self, review: str):

        model = fasttext.load_model(FAST_TEXT_MODEL)
        result = model.predict(text=review, threshold=0.5)
        isNeg = (result[0][0] == '__label__0')
        score = result[1][0]
        print(isNeg)
        print(score)



class SentimentModel(object):
    def __init__(self):
        self.model = fasttext.load_model(FAST_TEXT_MODEL)

    def preview(self, review: str):
        result = self.model.predict(text=review, threshold=0.5)
        isNeg = (result[0][0] == '__label__0')
        score = result[1][0]
        print(isNeg)
        print(score)
        return {'isNeg': isNeg, 'score': "{:.4f}".format(score)}



if __name__ == "__main__":
    # build_model_data()
    # train_test_split()
    # fast = FastText()
    # fast.train()
    fast_predict = SentimentModel()
    # fast_predict.preview('Tastes great')

    fast_predict.preview("Poor service and food is not tasty")