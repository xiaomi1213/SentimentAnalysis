# coding: utf-8

"""
问答主程序，循环向用户提供问答服务
"""

from topAspects import Business
import pandas as pd

business_id_df = pd.read_csv(r"..\data\business_id.csv",sep="\t")

flag = True
while flag:
    name = input("please input business name: ")
    ids = business_id_df.loc[business_id_df['name']==name,'id']
    print('Reviews that you are looking for')
    business = Business(ids, name)
    business.extract_aspects().aspect_based_summary()
    ans = input('Search again? yes/no: ')

    if ans == 'yes':
        flag = True
    elif ans == 'no':
        flag = False
        print('byebye')
    else:
        print('please input yes/no')
        continue

