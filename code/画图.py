import csv

import numpy as np
import pandas as pd
import re
from snownlp import SnowNLP
import datetime


def emotion_map(file_name):
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')

    sim = data['IP属地']

    for i in range(0, len(sim)):
        if sim[i] == np.nan:
            # 删除整行数据
            data = data.drop(i, axis=0)  # 注意：drop() 方法不改变原有的 df 数据！

    # location_p = data['发布者地理位置'].values
    location_p = data['IP属地'].values
    # location_c = data['一级地理位置'].values
    location_c = data['评论属地'].values

    for i in range(0, len(location_p)):
        print(location_p[i])
        print(type(location_p[i]))
        if location_p[i] == np.nan:
            continue
        if 'IP' in location_p[i]:
            location_p[i] = re.findall(r'IP属地：(\S+)', location_p[i])
            location_p[i] = ''.join(location_p[i])
        else:
            location_p[i] = location_p[i][0:2]
        if len(location_c[i]) >= 4:
            location_c[i] = location_c[i][0:2]
        else:
            location_c[i] = location_c[i]
    data.loc[len(data)] = data.columns
    data1 = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    comment = data['评论内容']
    tag = data['标记']
    m = 0
    len0 = 0
    add_p = 0
    add_c = 0
    ave_sp = 0
    loc_p = data1['IP属地'][0:len(data1) - 1].values
    d = {}
    for loc in loc_p:
        d[loc] = 0
    for j in range(0, len(comment)):
        comment[j] = ''.join(comment[j].split())  # 去除待情绪分析语料中的空格，防止情绪分析失败
        s = SnowNLP(comment[j])
        score = s.sentiments
        score = score * 2 - 1
        if tag[j] == 0:  # 一级评论
            #print(j,data1.index[m])
            if j <= data1.index[m]:
                add_p += score
                len0 += 1
            else:
                ave_sp = add_p / len0
                if d[loc_p[m]] != 0:
                    ave_sp = (ave_sp + d[loc_p[m]]) / 2
                    d[loc_p[m]] = ave_sp
                else:
                    d[loc_p[m]] = ave_sp
                add_p = 0
                len0 = 1
                add_p += score
                m += 1
        elif tag[j] == '标记':
            ave_sp = add_p / len0
            if d[loc_p[m]] != 0:
                ave_sp = (ave_sp + d[loc_p[m]]) / 2
                d[loc_p[m]] = ave_sp
            else:
                d[loc_p[m]] = ave_sp

    len1 = 0  # 计算二级评论个数
    loc = ''
    for j in range(0, len(comment)):
        comment[j] = ''.join(comment[j].split())  # 去除待情绪分析语料中的空格，防止情绪分析失败
        s = SnowNLP(comment[j])
        score = s.sentiments
        score = score * 2 - 1
        if tag[j] == 0:
            loc = location_c[j]
            if location_c[j] not in loc_p:
                d.update({location_c[j]: 0})
        elif tag[j] == 1:
            add_c += score
            len1 += 1
            if tag[j + 1] != 1:
                if d[loc] != 0:
                    ave_sp = (ave_sp + d[loc]) / 2
                    d[loc] = ave_sp
                else:
                    d[loc] = ave_sp
                len1 = 0
                add_c = 0
    return d


def read_data():
    data1 = pd.read_csv('帖子综合群体情绪.csv', encoding='utf-8', sep=';')
    df1 = data1.sort_values(by="群体情绪", ascending=True)
    df1 = df1.loc[:, ['发布者', '群体情绪']]
    emotion = df1['群体情绪'].values
    title = df1['发布者'].values
    emotion_p = []
    title_p = []
    emotion_n = []
    title_n = []
    for i in range(0, len(emotion)):
        title[i] = title[i].replace('\n', '')
        if emotion[i] >= 0:
            emotion_p.append(emotion[i])
            title_p.append(title[i])
        else:
            emotion_n.append(emotion[i])
            title_n.append(title[i])
    return title_p, emotion_p, title_n, emotion_n


def cluster_density():
    data = pd.read_csv('宏观集群密度.csv', encoding='utf-8', sep=';')
    df = data.sort_values(by="集群密度", ascending=True)
    den = df['集群密度'].values
    title = df['发布者'].values
    title_d = []
    density = []
    for i in range(0, len(title)):
        title_d.append(title[i])
        density.append(den[i])
        title_d[i] = title_d[i].replace('\n', '')
    return title_d, density


def change_date(times):
    time2 = []
    for time1 in times:
        time1 = str(time1)[:10]
        time2.append(time1)
    return time2


def emotion_tendency(file_name):
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    data['评论时间'] = change_date(data['评论时间'].values)
    df = data.sort_values(by="评论时间", ascending=True)
    times1 = df['评论时间'].values
    comment = data['评论内容'].values
    d_p = {}
    d_z = {}
    d_n = {}
    vb = 0.1
    times = []
    for time1 in times1:
        # time1 = str(time1)[:10]
        times.append(time1)
        d_p[time1] = 0
        d_z[time1] = 0
        d_n[time1] = 0
    for j in range(0, len(comment)):
        comment[j] = ''.join(comment[j].split())  # 去除待情绪分析语料中的空格，防止情绪分析失败
        s = SnowNLP(comment[j])
        score = s.sentiments
        score = score * 2 - 1
        if score > vb:
            d_p[times[j]] += 1
        elif vb > score > -vb:
            d_z[times[j]] += 1
        else:
            d_n[times[j]] += 1
    return d_p, d_z, d_n


def emotion_pie(file_name):
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    com_num = data['评论数'].values
    tran_num = data['转发数'].values
    like_num = data['点赞数'].values
    clike_num = data['评论点赞数'].values
    comment = data['评论内容'].values
    data1 = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    title = data1['发布者'].values
    p_p = {}
    p_p['评论'] = 0
    p_p['转发'] = 0
    p_p['点赞'] = 0
    p_n = {}
    p_n['评论'] = 0
    p_n['转发'] = 0
    p_n['点赞'] = 0
    for i in range(0, len(title)):
        title[i] = ''.join(title[i].split())  # 去除待情绪分析语料中的空格，防止情绪分析失败
        s = SnowNLP(title[i])
        score = s.sentiments
        score = score * 2 - 1
        if score > 0:
            p_p['评论'] += com_num[data1.index[i]]
            p_p['转发'] += tran_num[data1.index[i]]
            p_p['点赞'] += like_num[data1.index[i]]
        else:
            p_n['评论'] += com_num[data1.index[i]]
            p_n['转发'] += tran_num[data1.index[i]]
            p_n['点赞'] += like_num[data1.index[i]]
    for j in range(0, len(comment)):
        comment[j] = ''.join(comment[j].split())  # 去除待情绪分析语料中的空格，防止情绪分析失败
        s = SnowNLP(comment[j])
        score = s.sentiments
        score = score * 2 - 1
        if score > 0:
            p_p['评论'] += clike_num[j]
        else:
            p_n['点赞'] += clike_num[j]
    return p_p, p_n


if __name__ == '__main__':
    # filename = input('请输入待处理的文件：')
    filename = 'clean-微博电磁辐射数据.csv'
    emotion_map(filename)
