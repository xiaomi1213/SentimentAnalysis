# coding: utf-8

"""
一些工具函数，包括分词、获取前K个元素函数等。
"""

import re
import operator
from queue import PriorityQueue


# split sentence
def split_sentence(sentence: str):
    """
    split sentence base the punctuations
    :param sentence:
    :return:
    """
    return re.split("[;,.!?\\n]",sentence)


def add_to_dict_list(container:dict,key,value):
    if key in container:
        container[key].append(value)
    else:
        container[key] = [value]


class Item(object):
    def __init__(self, priority, content):
        super().__init__()
        self.priority = priority
        self.content = content

    def __lt__(self, other):
        return operator.lt(self.priority, other.priority)


def get_top_k(data, k):
    """
    get the top k items
    :param data:
    :param k:
    :return:
    """
    pq = PriorityQueue(maxsize=k)

    for key, value in data.items():
        if not pq.full():
            pq.put_nowait(Item(value,key))
        else:
            minor = pq.get_nowait()
            if minor.priority < value:
                pq.put_nowait(Item(value,key))
            else:
                pq.put_nowait(minor)
    ans = []
    while not pq.empty():
        ans.append(pq.get_nowait())
    return ans


def get_top_k_from_list(data:list,k:int):
    """
    get the top k from list
    :param data:
    :param k:
    :return:
    """
    pq = PriorityQueue(maxsize=k)

    for value in data:
        if not pq.full():
            pq.put_nowait(value)
        else:
            minor = pq.get_nowait()
            if minor.priority < value.priority:
                pq.put_nowait(value)
            else:
                pq.put_nowait(minor)
    ans = []
    while not pq.empty():
        ans.append(pq.get_nowait())
    return ans


def contains_related_aspect(aspect:str, sentence:str):
    """
    check if the aspect  in the sentence
    :param aspect:
    :param sentence:
    :return:
    """
    if re.search(aspect, sentence.lower()) is None:
        return False
    else:
        return True




