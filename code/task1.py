# -*- coding: utf-8 -*-
import xlrd
import re
import pandas as pd
import math
import numpy as np


def cluster_density(file_name):
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    # data_simple = data.drop_duplicates(subset=['标题'], keep='last', inplace=False)
    data_simple = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    data.loc[len(data)] = data.columns
    # data1 = data.drop_duplicates(subset=['标题'], keep='last', inplace=False)
    data1 = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    all_comment = data_simple['评论数'].values
    tag = data['标记']
    # title = data_simple['标题'].values
    title = data_simple['发布者'].values
    # post_time = data_simple['评论时间'].values
    first_comment = []
    j = 0  # 每个帖子的起始位置
    second_len = 0  # 每个帖子的总二级评论数
    for i in range(0, len(tag)):
        if i == len(tag) - 1:
            first_comment.append(all_comment[j] - second_len)
        else:
            if i <= data1.index[j]:
                if tag[i] == 1:
                    second_len += 1
            elif i > data1.index[j]:
                first_comment.append(all_comment[j] - second_len)
                j += 1
                second_len = 0
    real_like = data_simple['点赞数'].values  # 帖子真实点赞数目
    edges1 = first_comment + real_like  # 边数
    max_edge1 = [max(edges1)] * len(edges1)  # 最大边数
    density1 = edges1 / max_edge1  # 集群密度
    # df1 = pd.DataFrame(list(zip(title, first_comment, real_like, edges1, max_edge1, density1)),
    #                    columns=['标题', '真实一级评论数', '真实点赞数',
    #                             '边数', '最大边数', '集群密度'])
    df1 = pd.DataFrame(list(zip(title, first_comment, real_like, edges1, max_edge1, density1)),
                       columns=['发布者', '真实一级评论数', '真实点赞数',
                                '边数', '最大边数', '集群密度'])
    # df1 = df1.drop_duplicates()
    df1.to_csv('宏观集群密度.csv', sep=';', encoding='utf-8', index=False, mode='w+')
    # 微观集群密度
    comment_like = data['评论点赞数']
    num = 0
    i = 0
    real_comment_like = []
    f_label = []
    f_comment = []
    comment = data['评论内容']
    second_comment = []
    while i < len(tag) - 1:
        if tag[i] == 0:
            if tag[i+1] == 1:
                real_comment_like.append(comment_like[i])
                f_label.append(i)
                f_comment.append(comment[i])
                for j in range(1, len(tag) - i):
                    if tag[i + j] == 1:
                        num += 1
                    else:
                        second_comment.append(num)
                        i += 1
                        break
                i += num
                num = 0
            else:
                i += 1
        else:
            i += 1
    edges2 = np.array(second_comment) + np.array(real_comment_like)
    max_edge2 = np.repeat([max(edges2)], len(edges2))
    density2 = np.array(edges2) / np.array(max_edge2)
    df2 = pd.DataFrame(list(zip(f_label, f_comment, second_comment, real_comment_like, edges2, max_edge2, density2)),
                       columns=['label', '一级评论', '真实二级评论数', '真实点赞数',
                                '边数', '最大边数', '集群密度'])
    df2.to_csv('微观集群密度.csv', sep=';', encoding='utf-8', index=False, mode='w+')
    print('task1 finish')


if __name__ == '__main__':
    # filename = input('请输入待处理的文件：')
    filename = 'test.xlsx'
    cluster_density(filename)
