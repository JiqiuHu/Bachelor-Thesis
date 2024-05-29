# -*- coding: utf-8 -*-
import task1
import task2
import task3
import task4
import platform
import time
import os



def emotion_analysis(filename):
    for i in range(0, 10):
        #filename = f'/Users/mac/Desktop/2022-8-24 工作/code/weibo电磁辐射数据.csv'
        print('系统:', platform.system())
        T1 = time.perf_counter()
        task1.cluster_density(filename)
        task2.evaluates_senti(filename)
        task3.cluster_trust(filename)
        task4.group_emotion(filename)
        T2 = time.perf_counter()
        print('程序运行时间:%s秒' % (T2 - T1))
        print(f'文件{i}完成')


if __name__ == '__main__':
    os.system('python3 all_get.py')
    print('---------------------------------------------------------------')
    print("情绪计算开始：")
    filename = input('请输入待处理的文件：')
    emotion_analysis(filename)
