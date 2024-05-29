# -*- coding: utf-8 -*-
import xlrd
import re
import urllib
import csv
import time
import numpy as np
import pandas as pd
from random import randint


def group_emotion(file_name):
    # 读取输入文件
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    # data_simple = data.drop_duplicates(subset=['标题'], keep='last', inplace=False)
    data_simple = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    data1 = pd.read_csv('宏观集群密度.csv', sep=';')
    data2 = pd.read_csv('宏观集群平均情绪.csv', sep=';')
    data3 = pd.read_csv('宏观集群信任度值.csv', sep=';')
    all_density = data1['集群密度'].values
    average_emo = data2['帖子平均情绪值'].values
    all_average_emo = np.array(average_emo)
    all_average_emo = all_average_emo[~np.isnan(all_average_emo)]
    cre = data3['归一化信任度值'].values
    all_cre = []
    for i in range(0, len(cre)):
        if data3['发布者'][i] == '-----':
            all_cre.append(cre[i])
    # title = data3['标题']
    title = data_simple['发布者'].values
    post_time = data3['评论时间']
    emo_index = all_density * all_average_emo * all_cre
    # 群体情绪指数1归一化
    max_emo_index = max(emo_index)
    min_emo_index = min(emo_index)
    max_emo = max(abs(max_emo_index), abs(min_emo_index))
    emo_index = emo_index / max_emo

    data4 = pd.read_csv('微观集群密度.csv', sep=';')
    data5 = pd.read_csv('微观集群平均情绪.csv', sep=';')
    data6 = pd.read_csv('微观集群信任度值.csv', sep=';')
    micro_density = data4['集群密度'].values
    average_emo1 = data5['一级评论平均情绪值'].values
    first_average_emo = np.array(average_emo1)
    first_average_emo = first_average_emo[~np.isnan(first_average_emo)]
    cre1 = data6['归一化信任度值'].values
    label = data4['label'].values
    # comment = data6['一级评论']
    # 微观集群群体情绪
    micro_cre = np.array(cre1)
    micro_cre = micro_cre[~np.isnan(micro_cre)]
    micro_emo = micro_density * first_average_emo * micro_cre
    micro_emo_index = []
    j = 0
    temp = 0
    for i in range(0, len(data_simple)):
        if j == len(label):
            micro_emo_index.append(temp)
            temp = 0
        else:
            while label[j] < data_simple.index[i]:
                temp += micro_emo[j]
                j += 1
                if j == len(label):
                    break
            micro_emo_index.append(temp)
            temp = 0
    # 微观集群群体情绪指数
    micro_emo_index = np.array(micro_emo_index)
    max_mirco_emo_index = max(micro_emo_index)
    min_micro_emo_index = min(micro_emo_index)
    max_mirco_emo = max(abs(max_mirco_emo_index), abs(min_micro_emo_index))
    micro_emo_index = micro_emo_index / max_mirco_emo

    index1 = 0.6
    index2 = 0.4
    group_emo = index1 * emo_index + index2 * micro_emo_index
    # 群体情绪归一化
    max_group_emo_index = max(group_emo)
    min_group_emo_index = min(group_emo)
    max_group_emo = max(abs(max_group_emo_index), abs(min_group_emo_index))
    group_emo = group_emo / max_group_emo
    # 计算帖子综合群体情绪
    ave_emo = np.nansum(np.array(group_emo)) / len(group_emo)
    # 写入
    with open('宏观群体情绪.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f1:
        with open('微观群体情绪.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f2:
            with open('帖子综合群体情绪.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f3:
                writer1 = csv.writer(f1, delimiter=';')
                writer2 = csv.writer(f2, delimiter=';')
                writer3 = csv.writer(f3, delimiter=';')
                writer1.writerow(['发布者', '宏观集群密度', '帖子平均情绪值', '宏观集群信任度值', '群体情绪指数1'])
                writer2.writerow(['微观集群密度', '一级评论平均情绪值', '微观集群信任度值', '微观集群群体情绪', '群体情绪指数2'])
                writer3.writerow(['发布者', '群体情绪', '时间'])
                n = 0
                for j in range(0, len(data_simple)):
                    if n == len(label):
                        pass
                    else:
                        while label[n] < data_simple.index[j]:
                            writer2.writerow([micro_density[n], first_average_emo[n], micro_cre[n], micro_emo[n]])
                            n += 1
                            if n == len(label):
                                break
                    writer2.writerow(
                        ['--------', '--------', '--------', '--------', micro_emo_index[j]])
                    writer1.writerow([title[j], all_density[j], all_average_emo[j], all_cre[j], emo_index[j]])
                    writer3.writerow([title[j], group_emo[j], post_time[j]])

    with open('事件或节目整体群体情绪.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f4:
        writer4 = csv.writer(f4, delimiter=';')
        writer4.writerow(['整体情绪'])
        writer4.writerow([ave_emo])
    print('task4 finish')


if __name__ == '__main__':
    # filename = input('请输入待处理的文件：')
    filename = 'test.xlsx'
    group_emotion(filename)
