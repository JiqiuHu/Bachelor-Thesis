# -*- coding: utf-8 -*-
import xlrd
import re
# import urllib
import csv
import time
import numpy as np
import pandas as pd
from snownlp import SnowNLP


def evaluates_senti(file_name):
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    data.loc[len(data)] = data.columns
    # data1 = data.drop_duplicates(subset=['标题'], keep='last', inplace=False)
    data1 = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    sours = data['评论内容']
    # title = data['标题']
    title = data['发布者']
    post_time = data['评论时间']
    tag = data['标记']
    # 平均值
    average_score1 = 0
    average_score2 = 0
    j = 0
    len0 = 0
    len1 = 0
    comment = ''
    with open('宏观集群平均情绪.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f1:
        with open('微观集群平均情绪.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f2:
            with open('error.csv', 'a', errors='ignore', newline='', encoding='utf-8') as f3:
                writer1 = csv.writer(f1, delimiter=';')
                writer2 = csv.writer(f2, delimiter=';')
                writer3 = csv.writer(f3, delimiter=';')
                writer3.writerow(['序号', '评论内容', '情绪分数'])
                writer1.writerow(['发布者', '实际爬取到的一级评论内容', '评论时间', '单条评论情绪值', '帖子平均情绪值'])
                writer2.writerow(['一级评论', '实际爬取到的二级评论内容', '单条评论情绪值', '一级评论平均情绪值'])
                for i in range(0, len(sours)):
                    try:
                        sours[i] = ''.join(sours[i].split())  # 去除待情绪分析语料中的空格，防止情绪分析失败
                        s = SnowNLP(sours[i])
                        score = s.sentiments
                        score = score * 2 - 1
                        if tag[i] == 0:  # 计算帖子的一级评论平均情绪值
                            comment = sours[i]
                            if i <= data1.index[j]:
                                average_score1 += float(score)
                                len0 += 1
                                writer1.writerow([title[i], sours[i], post_time[i], score])
                            elif i > data1.index[j]:
                                if len0 == 0:
                                    average_score1 = 0000000
                                else:
                                    average_score1 = average_score1 / len0
                                writer1.writerow(['-------', '--------', '--------', '--------', average_score1])
                                writer1.writerow([title[i], sours[i], post_time[i], score])
                                average_score1 = float(score)
                                j += 1
                                len0 = 1
                        elif tag[i] == 1:  # 计算一级评论下二级评论的平均情绪值
                            len1 += 1
                            average_score2 += float(score)
                            writer2.writerow([comment, sours[i], score])
                            if tag[i + 1] != 1:
                                average_score2 = average_score2 / len1
                                writer2.writerow(['-------', '--------', '--------', average_score2])
                                average_score2 = 0
                                len1 = 0
                            else:
                                pass
                        else:
                            if len0 == 0:
                                average_score1 = 0000000
                            else:
                                average_score1 = average_score1 / len0
                            writer1.writerow(['-------', '--------', '--------', '--------', average_score1])
                    except:
                        writer3.writerow(sours[i])
                        writer3.writerow(sours)
    print('task2 finish')


if __name__ == '__main__':
    # filename = input('请输入待处理的文件：')
    filename = 'test.xlsx'
    evaluates_senti(filename)
