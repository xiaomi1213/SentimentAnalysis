# coding: utf-8

"""
数据预处理：按business_id将review分组到每个子文件。
"""

import pandas as pd
import json
import os
from collections import defaultdict

# extract business_id and name from business.json
business_file = open(r"..\data\business_id.csv","w",encoding='utf8')
with open(r"..\data\business.json","r",encoding='utf8') as f:
    business_file.write("business_id"+"\t"+"name"+"\n")
    for line in f:
        line_data = json.loads(line.strip())
        business_file.write(line_data["business_id"]+"\t"+line_data["name"]+"\n")
business_file.close()

# store id_name data with dict
business_id_name_dict = {}
with open(r"..\data\business_id.csv","r",encoding="utf8") as f:
    next(f) # skip the first line
    for line in f:
        lines = line.strip().split('\t')
        business_id_name_dict[lines[0]] = lines[1]


# get the business_id list
business_id_df = pd.read_csv(r"..\data\business_id.csv",sep="\t")
business_id_list = list(set(business_id_df["business_id"]))

# filter out the business whose review is less than 100, and group the reviews by business
split_data_path = "..\data\split_data"
split_data_dict = defaultdict(list)
with open(r"..\data\review.json","r", encoding='utf8') as f:
    for line in f:
        line_data = json.loads(line.strip())
        split_data_dict[line_data['business_id']].append(line.strip())

print('filting.......')
for key, value in split_data_dict.items():
    if len(value) >= 100:
        each_file = os.path.join(split_data_path, key + ".txt")
        with open(each_file, "a", encoding="utf8") as f:
            for line in value:
                f.write(line+'\n')






















