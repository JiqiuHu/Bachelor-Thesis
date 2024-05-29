import xlrd
import re
import urllib
import csv
import time
import numpy as np
import pandas as pd
from random import randint


def cluster_trust(file_name):
    # 读取输入文件
    if 'xlsx' in file_name:
        data = pd.read_excel(file_name)
    else:
        data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    data1 = pd.read_csv('宏观集群平均情绪.csv', sep=';')
    data2 = pd.read_csv('微观集群平均情绪.csv', sep=';')
    # data_simple = data.drop_duplicates(subset=['标题'], keep='last', inplace=False)
    data_simple = data.drop_duplicates(subset=['发布者'], keep='last', inplace=False)
    emo1 = data1['单条评论情绪值'].values
    emo2 = data2['单条评论情绪值']
    # title1 = data1['标题']
    title1 = data1['发布者']
    post_time = data1['评论时间']
    comment1 = data1['实际爬取到的一级评论内容']
    # 信任指数1
    cre1 = []
    # 信任指数2
    cre2 = []
    # 标准差
    var0 = []
    var1 = []
    # 正向情绪最大值
    f_max1 = []
    b_max1 = []
    diff1 = []
    for i in range(0, len(emo1)):
        if emo1[i] == '--------':
            sd0 = np.std(var0, ddof=0)
            cre1.append(sd0)
            max0 = max(var0)
            min0 = min(var0)
            if max0 < 0:
                f_temp = None
            else:
                f_temp = max0
            f_max1.append(f_temp)
            if min0 > 0:
                b_temp = None
            else:
                b_temp = min0
            b_max1.append(b_temp)
            if f_temp and b_temp:
                di0 = f_temp - b_temp
            else:
                di0 = 0
            diff1.append(di0)
            # 信任度指数2
            temp = (2 - di0) / 2
            cre2.append(temp)
            var0 = []
        else:
            var0.append(float(emo1[i]))
    # 信任指数3
    trans = data_simple['转发数'].values
    max_trans = max(trans)
    cre3 = trans / max_trans
    # 信任度指数4
    fan_num = data_simple['帖子账号粉丝数'].values
    max_fan = max(fan_num)
    cre4 = fan_num / max_fan
    cre4 = cre4.tolist()
    # 信任度值
    cre = []
    for j, element in enumerate(cre4):
        if np.isnan(cre4[j]):
            # 指数
            index1 = 0.4
            index2 = 0.4
            index3 = 0.2
            cre.append(index1 * cre1[j] + index2 * cre2[j] + index3 * cre3[j])
        else:
            index1 = 0.35
            index2 = 0.35
            index3 = 0.2
            index4 = 0.1
            cre.append(index1 * cre1[j] + index2 * cre2[j] + index3 * cre3[j] + index4 * cre4[j])
    # 宏观归一化
    # real_cre = cre
    max_cre = max(cre)
    real_cre = cre / max_cre

    comment = data2['一级评论']
    comment2 = data2['实际爬取到的二级评论内容']
    f_max2 = []
    b_max2 = []
    diff2 = []
    cre5 = []
    cre6 = []
    for j in range(0, len(emo2)):
        if emo2[j] == '--------':
            sd1 = np.std(np.array(var1), ddof=0)
            # 信任度指数1
            cre5.append(sd1)
            max1 = max(var1)
            min1 = min(var1)
            if max1 < 0:
                f_temp = None
            else:
                f_temp = max1
            f_max2.append(f_temp)
            if min1 > 0:
                b_temp = None
            else:
                b_temp = min1
            b_max2.append(b_temp)
            if f_temp and b_temp:
                di1 = f_temp - b_temp
            else:
                di1 = 0
            diff2.append(di1)
            # 信任度指数2
            temp = (2 - di1) / 2
            cre6.append(temp)
            var1 = []
        else:
            var1.append(float(emo2[j]))
    # 信任度指数3：一级评论真实被转发数
    # comment_like = data['评论点赞数']
    # try:
    #     first_trans = data['评论转发数']
    # except:
    #     first_trans = []
    tag = data['标记']
    # 信任度指数4：一级评论账号粉丝数
    first_fan = []
    for k in range(0, len(tag)-1):
        if tag[k] == 0:
            if tag[k + 1] == 1:
                first_fan.append(data['一级账号粉丝数'][k])
    max_first_fan = max(first_fan)
    cre8 = np.array(first_fan) / max_first_fan
    # 信任度值
    cre9 = []
    for n in range(0, len(first_fan)):
        if np.isnan(first_fan[n]):
            index1 = 0.5
            index2 = 0.5
            cre9.append(index1 * cre5[n] + index2 * cre6[n])
        else:
            index1 = 0.4
            index2 = 0.4
            index3 = 0.2
            cre9.append(index1 * cre5[n] + index2 * cre6[n] + index3 * cre8[n])
    # 归一化
    max_cre1 = max(cre9)
    real_cre1 = cre9 / max_cre1
    # real_cre1 = cre9
    # 写入
    with open('宏观集群信任度值.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f1:
        with open('微观集群信任度值.csv', 'w+', errors='ignore', newline='', encoding='utf-8') as f2:
            writer2 = csv.writer(f2, delimiter=';')
            writer1 = csv.writer(f1, delimiter=';')
            writer1.writerow(['发布者', '实际爬取到的一级评论内容', '评论时间', '单条评论情绪值', '信任度指数1', '正向情绪最大绝对值', '负向情绪最大绝对值',
                              '情绪极性差值', '信任度指数2', '帖子的真实被转发数', '信任度指数3', '帖子账号的粉丝数',
                              '信任度指数4', '信任度值', '归一化信任度值'])
            writer2.writerow(['一级评论', '实际爬取到的二级评论内容', '单条评论情绪值', '信任度指数1', '正向情绪最大绝对值', '负向情绪最大绝对值',
                              '情绪极性差值', '信任度指数2', '一级评论账号的粉丝数',
                              '信任度指数4', '信任度值', '归一化信任度值'])
            m = 0
            for i in range(0, len(emo1)):
                if emo1[i] == '--------':
                    writer1.writerow(['-----', '------', '------', '------', cre1[m], f_max1[m], b_max1[m], diff1[m], cre2[m], trans[m],
                                      cre3[m], fan_num[m], cre4[m], cre[m], real_cre[m]])
                    m += 1
                else:
                    writer1.writerow([title1[i], comment1[i], post_time[i], emo1[i]])
            n = 0
            for i in range(0, len(emo2)):
                if emo2[i] == '--------':
                    writer2.writerow(['-----', '------', '------', cre5[n], f_max2[n], b_max2[n], diff2[n], cre6[n],
                                      first_fan[n], cre8[n], cre9[n], real_cre1[n]])
                    n += 1
                else:
                    writer2.writerow([comment[i], comment2[i], emo2[i]])
    print('task3 finish')


if __name__ == '__main__':
    # filename = input('请输入待处理的文件：')
    filename = 'test.xlsx'
    cluster_trust(filename)
