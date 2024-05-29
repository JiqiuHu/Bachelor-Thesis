import streamlit as st
import main
import test
import csv
import time
import pandas as pd
import re
import all_get
import numpy as np
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

def initial():
    global keyword
    keyword = None
    global website
    website = None
    global key
    key = None
    global web
    web = None
    global uploaded_file1
    uploaded_file1 = None
    global uploaded_file2
    uploaded_file2 = None

def douyin_slide():
    # temp_height = 1
    for j in range(1, 200):
        driver.execute_script("scrollBy(0,10000)")  # 执行拖动滚动条操作
        # check_height = driver.execute_script(
        #     "return document.documentElement.scrollTop || document.body.scrollTop;")
        time.sleep(2)
        try:
            end = driver.find_element_by_xpath("//div[@class='_5711aa3bb8cc604a63af009da08a1e20-scss']").text
            if "没有" in end:
                break
        except:
            continue

def kuaishou_slide():
    for j in range(1, 200):
        time.sleep(2)
        driver.execute_script("scrollBy(0,10000)")
        try:
            end = driver.find_element_by_xpath("//div[@class='spinning search-loading']").text
            if '已经到底了' in end:
                break
        except:
            continue


side_bar = st.sidebar.radio(
    '网络舆论分析系统：',
    ['爬取链接', '爬取数据','群体情绪计算', '结果分析']
)

# ========================================================================================
if side_bar == '爬取链接':
    initial()
    st.title('爬取链接')

    keyword = st.text_input('请输入爬取的关键词:')
    website = st.selectbox(
        '请选择要爬取的网站:',
        ('0','微博', '哔哩哔哩','抖音'))

#爬取微博帖子url
    if website == '微博':
        file = '微博' + keyword + '.csv'
        date = st.text_input('请输入起止时间(eg.2021-09-01-0:2022-03-08-23):')
        if date:
            st.info('请前往微博页面完成登陆')
            weibo_url = 'https://s.weibo.com/'
            s = Service(r"/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=s)
            driver.get(weibo_url)
            time.sleep(30)

            with open(file, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
                titles = ["发布者", "发布时间", "博客url链接"]
                writer = csv.DictWriter(fp, fieldnames=titles, delimiter=';')
                writer.writeheader()
                for i in range(1, 50):
                    try:
                        w_url = f"https://s.weibo.com/weibo?q={keyword}&timescope=custom:{date}&Refer=g&sudaref=s.weibo.com&page={i}"
                        # w_url = f"https://s.weibo.com/weibo?q={self.keyword}&typeall=1&hasvideo=1&timescope=custom:{date}&Refer=g&page={i}"
                        driver.get(w_url)
                        driver.implicitly_wait(10)
                        blogs = driver.find_elements(By.XPATH, "//div[@class='main-full']//div[@class='card-wrap']")
                        if blogs:
                            for blog in blogs:

                                publish_time = blog.find_element(By.CSS_SELECTOR,
                                                                 "div.from> a:nth-child(1)").text
                                up_name = blog.find_element(By.CSS_SELECTOR, ".name").text
                                try:
                                    blog_url = blog.find_element(By.CSS_SELECTOR,
                                                                 "div.from> a:nth-child(1)").get_attribute('href')
                                except:
                                    blog_url = 'NULL'
                                writer.writerow({"发布者": up_name, "发布时间": publish_time, "博客url链接": blog_url})

                        else:
                            st.warning('爬取失败')
                    except:
                        st.warning('一共爬取了'+str(i-1)+'页,'+'页数' + str(i) + '不存在')
                        break

            driver.close()
            st.success('爬取结束，数据保存为：{}'.format(file))

            data1 = pd.read_csv(file, encoding='utf-8', sep=';',engine = "python")
            st.write(data1)


    if website == '哔哩哔哩':
        file5 = '哔哩哔哩' + keyword + '.csv'
        duration = st.text_input('请输入视频时长(全部：0，10min以下：1，10-30min：2，30-60min：3，60min以上：4):')
        if duration:
            s = Service(r"/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=s)
            with open(file5, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
                titles = ["标题", "发布者", "发布时间", "观看数", "urls", "视频时长"]
                writer = csv.DictWriter(fp, fieldnames=titles, delimiter=';')
                writer.writeheader()
                for i in range(1, 50):
                    try:
                        b_url = f"https://search.bilibili.com/video?keyword={keyword}&duration={int(duration)}&page={i}"
                        driver.get(b_url)
                        driver.implicitly_wait(10)
                        videos = driver.find_elements_by_xpath("//li[@class='video-item matrix']")
                        if videos:
                            for video in videos:
                                video_url = video.find_element_by_css_selector('a.img-anchor').get_attribute(
                                    'href')
                                publish_time = video.find_element_by_css_selector("span.so-icon.time").text
                                up_name = video.find_element_by_css_selector("a.up-name").text
                                title = video.find_element_by_css_selector("a.title").text
                                view_number = video.find_element_by_css_selector("span.so-icon.watch-num").text
                                length = video.find_element_by_css_selector("span.so-imgTag_rb").text
                                writer.writerow(
                                    {"标题": title, "发布者": up_name, "发布时间": publish_time, "观看数": view_number,
                                     "urls": video_url, "视频时长": length})
                        else:
                            st.warning('爬取失败')
                    except:
                        st.warning('一共爬取了'+str(i-1)+'页,'+'页数' + str(i) + '不存在')
                        break

            driver.close()
            st.success('爬取结束，数据保存为：{}'.format(file5))

            data5 = pd.read_csv(file5, encoding='utf-8', sep=';', engine="python")
            st.write(data5)

    if website == '抖音':
        file6 = '抖音' + keyword + '.csv'
        date1 = st.text_input('请输入爬虫时间范围(0为不限制1为1天内发布的7为一周内182为半年内)：')
        if date1:
            st.info('请前往抖音页面完成登陆')
            douyin_url = f'https://www.douyin.com/search/{keyword}?publish_time={date1}&sort_type=0&source=normal_search&type=video'
            s = Service(r"/usr/local/bin/chromedriver")
            driver = webdriver.Chrome(service=s)
            driver.get(douyin_url)
            time.sleep(30)
            douyin_slide()

            with open(file6, "a+", errors="ignore", newline='', encoding='utf-8') as f:
                titles = ['视频标题', 'urls', '发布者', '发布时间', '视频长度', '视频点赞数']
                writer = csv.DictWriter(f, fieldnames=titles, delimiter=';')
                writer.writeheader()
                driver.implicitly_wait(10)
                videos = driver.find_elements_by_xpath("//li[@class='a3cc5072a10a34f3d46c4e722ef788c1-scss']")
                if videos:
                    for video in videos:
                        # 视频标题
                        try:
                            title = video.find_element_by_css_selector(
                                "._1d72ef4c67644daab0f1496c89e038aa-scss.b2c8df63da2ed9be2bc3d38cf902e5b4-scss").text
                            # 视频链接
                            every_url = video.find_element_by_css_selector(
                                ".caa4fd3df2607e91340989a2e41628d8-scss.a074d7a61356015feb31633ad4c45f49-scss.b388acfeaeef33f0122af9c4f71a93c9-scss").get_attribute(
                                'href')
                            post = video.find_element_by_css_selector(
                                "._31dc42fa6181927e1afa821a0db10ed0-scss._7cfe89a4f1868679513e50ad5cf7215c-scss").text
                            post_time = video.find_element_by_css_selector(
                                ".b32855717201aaabd3d83c162315ff0a-scss").text
                            length = video.find_element_by_css_selector(".d170ababc38fdbf760ca677dbaa9206a-scss").text
                            like_num = video.find_element_by_css_selector(
                                "._04b09e32a7964282872626a4aff3353b-scss").text
                            writer.writerow({'视频标题': title, 'urls': every_url, '发布者': post, '发布时间': post_time, '视频长度':
                                length, '视频点赞数': like_num})
                        except:
                            pass
                else:
                    st.warning('爬取失败')

            driver.close()
            st.success('爬取结束，数据保存为：{}'.format(file6))

            data6 = pd.read_csv(file6, encoding='utf-8', sep=';', engine="python")
            st.write(data6)





# ========================================================================================
if side_bar == '爬取数据':
    initial()

    st.title('爬取数据')
    key = st.text_input('请输入爬取的关键词:')
    file2 = st.file_uploader("请上传爬取的url文件：")
    if file2 is not None:
        st.success('upload success!')
    else:
        st.error('upload failed!')

    cluster = pd.read_csv(file2, encoding='utf-8', sep=';')
    n = 0
    for i in range(0, cluster.shape[1]):
        sheet = cluster.iloc[:, i].values
        if re.match(r"(http|https|ftp)://\S+", str(sheet[0])):
            n = i
            break
        else:
            continue
    sheet = cluster.iloc[:, n].values

    web = website = st.selectbox(
        '请选择要爬取的网站:',
        ('0','微博', '哔哩哔哩','抖音'))



    if website == '微博':

        file1 = '微博' + key + '数据.csv'
        with open(file1, "a+", errors="ignore", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(
                ["发布者","IP属地","帖子账号粉丝数", "转发数", "评论数", "点赞数", "文本", "话题", "一级账号粉丝数","用户名","评论属地", "评论内容", "评论时间", "评论点赞数", "主题相似度" ,"标记"])
            rows = len(sheet)
            for i in range(0, rows):
                url = sheet[i]
                all_get.weibo(writer, url, 0,key)
                time.sleep(10)
                all_get.view_bar(i, rows)

            st.success("\n数据爬取结束，原始数据保存为：{}".format(file1))
            data2 = pd.read_csv(file1, encoding='utf-8', sep=';',dtype={'columnname': np.float64})
            st.write(data2)

            st.info('根据主题相似度过滤：')
            all_get.cleandata(file1)
            st.info("信息过滤完成,数据保存为：{}".format("clean-" + file1))
            clean_data = pd.read_csv(filepath_or_buffer="clean-" + file1, encoding='utf-8', sep=';')

            st.write(clean_data)


    if website == '哔哩哔哩':
        file2 = '哔哩哔哩' + key + '数据.csv'
        with open(file2, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(["标题", "发布者", "发布时间", "评论数", "用户名", "评论内容", "评论点赞数", "评论发表时间"])
            rows = len(sheet)
            for i in range(0, rows):
                url2 = sheet[i]
                time.sleep(3)
                all_get.kuaishou(writer, url2)
                all_get.view_bar(i, rows)

            st.success("\n数据爬取结束，原始数据保存为：{}".format(file2))
            data2 = pd.read_csv(file1, encoding='utf-8', sep=';', dtype={'columnname': np.float64})
            st.write(data2)

            st.info('根据主题相似度过滤：')
            all_get.cleandata(file1)
            st.info("信息过滤完成,数据保存为：{}".format("clean-" + file1))
            clean_data = pd.read_csv(filepath_or_buffer="clean-" + file1, encoding='utf-8', sep=';')

            st.write(clean_data)

    if website == '抖音':
        file3 = '抖音' + key + '数据.csv'
        with open(file3, "a+", errors="ignore", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(
                ["标题", "标题tag", "发布时间", "视频时长", "发布者", "发布者粉丝数量", "发布者是否蓝V", "发布者总点赞数量", "评论数", "收藏", "点赞", "用户名",
                 "评论内容", "评论时间", "评论点赞数", "评论回复数", "标记"])
            rows = len(sheet)
            # douyin_signin(sheet[0])
            for i in range(0, rows):
                url1 = sheet[i]
                getinfo = all_get.GetDouyinInfo(writer, url1)
                getinfo.douyin_crawl()
                all_get.view_bar(i, rows)

            st.success("\n数据爬取结束，原始数据保存为：{}".format(file2))
            data2 = pd.read_csv(file1, encoding='utf-8', sep=';', dtype={'columnname': np.float64})
            st.write(data2)

            st.info('根据主题相似度过滤：')
            all_get.cleandata(file1)
            st.info("信息过滤完成,数据保存为：{}".format("clean-" + file1))
            clean_data = pd.read_csv(filepath_or_buffer="clean-" + file1, encoding='utf-8', sep=';')

            st.write(clean_data)


    if website == '快手':
        file4 = '快手' + key + '数据.csv'
        with open(file4, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(["标题", "发布者", "发布时间", "评论数", "用户名", "评论内容", "评论点赞数", "评论发表时间"])
            rows = len(sheet)
            for i in range(0, rows):
                url2 = sheet[i]
                time.sleep(3)
                all_get.kuaishou(writer, url2)
                all_get.view_bar(i, rows)

            st.success("\n数据爬取结束，原始数据保存为：{}".format(file2))
            data2 = pd.read_csv(file1, encoding='utf-8', sep=';', dtype={'columnname': np.float64})
            st.write(data2)

            st.info('根据主题相似度过滤：')
            all_get.cleandata(file1)
            st.info("信息过滤完成,数据保存为：{}".format("clean-" + file1))
            clean_data = pd.read_csv(filepath_or_buffer="clean-" + file1, encoding='utf-8', sep=';')

            st.write(clean_data)




# ========================================================================================
if side_bar == '群体情绪计算':
    initial()
    st.title('群体情绪计算')
    uploaded_file1 = st.file_uploader("请上传爬取的文件")
    if uploaded_file1 is not None:
        st.success('upload success!')
    else:
        st.error('upload failed!')
    if st.button('开始计算'):
        main.emotion_analysis(uploaded_file1.name)
        st.write('计算结束')



# ========================================================================================
if side_bar == '结果分析':
    initial()
    st.title('结果分析')
    uploaded_file2 = st.file_uploader("请上传爬取的文件(请确保该数据的情绪计算结果保存在同一目录下）")
    if uploaded_file2 is not None:
        st.success('upload success!')
        #bo = st.selectbox('数据情感分析结果：',
                          #('群体情绪排行榜', '群体情绪中国地图', '集群密度排行', '点赞评论转发占比图', '群体情绪趋势图'))
        bo = st.selectbox('数据情感分析结果：',
                          ('群体情绪排行榜', '集群密度排行', '点赞评论转发占比图', '群体情绪趋势图'))
        test.analysis(bo, uploaded_file2)
    else:
        st.error('upload failed!')









