# -*- coding: utf-8 -*-
# 该代码文件作用：爬取某具体视频的评论内容
import requests
import json
import pandas as pd
import sys
import time
import selenium
from selenium import webdriver
import csv
import random
import re
from datetime import datetime
import math
import paddlehub as hub
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


lda_news = hub.Module(name="lda_news")
chrome_path = r"/usr/local/bin/chromedriver"
s = Service(r"/usr/local/bin/chromedriver")
scroll_js_5k = "scrollBy(0, 5000)"
scroll_js_10w = "scrollBy(0, 100000)"

# 获取浏览器
chrome_options = webdriver.ChromeOptions()
prefs = {'profile.managed_default_content_settings.images': 2}
driver = webdriver.Chrome(service=s)
# 下面代码用处：不加载图片。但由于滑块验证需要加载图片，故注释
# chrome_options.add_experimental_option('prefs', prefs)
# driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
#driver = webdriver.Chrome(service=s)

# 处理selenium中webdriver特征值
driver.execute_cdp_cmd(
    'Page.addScriptToEvaluateOnNewDocument',
    {
        'source': 'Object.defineProperty(navigator,"webdriver",{get:()=>undefined})'
    }
)

#driver.set_window_position(x=0, y=0)


def view_bar(num, total):
    rate = float(num) / float(total)
    rate_num = int(rate * 100)
    bar = '\r[%s%s]%d%%,%d' % ("=" * rate_num, "" * (100 - rate_num), rate_num, num)
    sys.stdout.write(bar)
    sys.stdout.flush()


def random_sleep(mu, sigma):
    secs = random.normalvariate(mu, sigma)
    if secs <= 0:
        secs = mu
        time.sleep(secs)


# 时间戳转时间
def timeStamp(timeNum):
    timestamp = float(timeNum / 1000)
    timeArray = time.localtime(timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


# GMT格式转换时间
def gmt_trans(dd):
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    time1 = datetime.strptime(dd, GMT_FORMAT)
    return time1

#新浪微博mid和url的互算
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)

def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num

def url_to_mid(url):
    '''
    >>> url_to_mid('z0JH2lOMb')
    3501756485200075L
    >>> url_to_mid('z0Ijpwgk7')
    3501703397689247L
    >>> url_to_mid('z0IgABdSn')
    3501701648871479L
    >>> url_to_mid('z08AUBmUe')
    3500330408906190L
    >>> url_to_mid('z06qL6b28')
    3500247231472384L
    >>> url_to_mid('yCtxn8IXR')
    3491700092079471L
    >>> url_to_mid('yAt1n2xRa')
    3486913690606804L
    '''
    url = str(url)[::-1]
    size = len(url) // 4 if len(url) % 4 == 0 else len(url) // 4 + 1
    result = []
    for i in range(size):
        s = url[i * 4: (i + 1) * 4][::-1]
        s = str(base62_decode(str(s)))
        s_len = len(s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append(s)
    result.reverse()
    return int(''.join(result))

# B站bv号转av号
def bv2av(bv_url):
    bv_num = re.findall(r'.+BV(.+)?from.+', bv_url)
    BV = ''.join(bv_num)
    # 密码表0-57
    table = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
    pows = [6, 2, 4, 8, 5, 9, 3, 7, 1, 0]
    bv_sum = 0
    for i in range(0, 10):
        for j in range(0, 58):
            if table[j] == BV[i]:
                # print(pows[k])
                res = j * math.pow(58, pows[i])
                bv_sum += int(res)
            else:
                continue
    bv_sum -= 100618342136696320
    temp = 177451812
    av = bv_sum ^ temp
    return av


def douyin_signin(sign_url):
    driver.get(sign_url)
    check = input('请检查网页状态(正常请输入1):')
    if check == '1':
        driver.delete_all_cookies()
        with open('douyin_cookies.txt', 'r') as f:
            # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookies_list = json.load(f)
            for cookie in cookies_list:
                cookie_dict = {
                    'domain': cookie.get('domain'),
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": '',
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False
                }
                driver.add_cookie(cookie_dict)
                time.sleep(2)
        driver.refresh()
        print('登陆完成')


class GetDouyinInfo:
    def __init__(self, writer1, url2):
        self.url = url2
        self.writer = writer1
        # self.sheet = sheet1

    @staticmethod
    def douyin_slide(stop1):
        res = 0
        stop1 += 1
        for j in range(1, 50):
            driver.execute_script("scrollBy(0,10000)")  # 执行拖动滚动条操作
            try:
                end = driver.find_element_by_xpath(
                    "//div[@class='KyLjQrjE QY8xxXiP']").text
                if end == '暂时没有更多评论':
                    res = 1
                    print('###################结束滑动#############################')
                    break
            except:
                try:
                    driver.find_element_by_xpath("//p[@class='BbQpYS5o HO1_ywVX']")
                    res = 1
                    break
                except:
                    res = 0
        return res, stop1

    @staticmethod
    def reply_comment(se_comment):
        # find_elements_by_xpath("//div[@class='c7ee22de401c856152e3646bffd656a3-scss']/div/button"):
        try:
            se_comment.find_element_by_css_selector("div[class='nNNp3deF']")
            reply_num = 1
        except:
            try:
                reply1 = se_comment.find_element_by_css_selector("button[class='zeyRYM2J']")
                print(reply1.text)
                if "展开" in reply1.text:
                    reply_num = re.findall(r'\d', reply1.text)
                    reply_num = int(''.join(reply_num))
                    reply1.send_keys(Keys.ENTER)
                # print(reply1.text)
                # reply1.find_element_by_css_selector('span').click()
                else:
                    reply_num = 0
            except:
                reply_num = 0
        return reply_num

    @staticmethod
    def get_douyin_info(writer):
        driver.implicitly_wait(10)
        # 发布者
        post = driver.find_element_by_xpath(
            "//div[@class='bQEtX7d8']//div[@class='yy223mQ8']//span[@class='Nu66P_ba']").get_attribute(
            'textContent')
        # print(post)
        # 视频评论数
        comment_count = driver.find_element_by_xpath(
            "//div[@class='UwvcKsMK']/div[2]").text
        # print(comment_count)
        # 视频标题
        title = driver.find_element_by_xpath("//h1").text
        # print(title)
        # 视频发布时间
        time_p = driver.find_element_by_xpath(
            "//span[@class='aQoncqRg']").text
        time1 = re.findall(r'\d', time_p)
        publish_time = "".join(time1)
        # print(publish_time)
        # 视频时长
        length = driver.find_element_by_xpath("//span[@class='time-duration']").text
        while length == '':
            time.sleep(1)
            length = driver.find_element_by_xpath("//span[@class='time-duration']").get_attribute('textContent')
        # print(length)
        # tag
        title_tag = []
        try:
            t_tags = driver.find_elements_by_xpath("//h1//span[@class='vStoQqaB']")
            for t_tag in t_tags:
                title_tag.append(t_tag.text)
            title_tag = ''.join(title_tag)
        except:
            pass
        # print(title_tag)
        # 收藏数
        star = driver.find_element_by_xpath("//div[@class='UwvcKsMK']/div[3]").text
        # print(star)
        # 点赞
        like = driver.find_element_by_xpath("//div[@class='UwvcKsMK']/div[1]").text
        # print(like)
        # 是否蓝V
        try:
            v = driver.find_element_by_xpath("//div[@class='TbVeDr9X NMQkGv7m']").text
            v_tag = 1
        except:
            v_tag = 0
        # 粉丝数
        fan_num = driver.find_element_by_xpath(
            "//div[@class='bQEtX7d8']//span[@class='EobDY8fd'][1]").get_attribute('textContent')
        # print(fan_num)
        # 总点赞数
        all_like = driver.find_element_by_xpath(
            "//div[@class='bQEtX7d8']//span[@class='EobDY8fd'][2]").get_attribute('textContent')
        # 视频下方评论
        res = 0
        if comment_count != 0:
            k = 0
            while res == 0:
                comments = driver.find_elements_by_xpath(
                    "//div[@class='CDx534Ub']")
                # j = 331
                for j in range(k, len(comments)):
                    stop = 0
                    # 评论用户名
                    user_name = comments[j].find_element_by_css_selector(
                        "div[class='nEg6zlpW']").text
                    # 评论内容
                    comment_content = comments[j].find_element_by_css_selector(
                        "span[class='VD5Aa1A1']").text
                    # 评论发布时间
                    time_c = comments[j].find_element_by_css_selector("p[class='dn67MYhq']").text
                    # 评论点赞数
                    like_num = comments[j].find_element_by_css_selector("p[class='eJuDTubq']").text
                    tag = 1
                    # "标题","标题tag","发布时间","视频时长","发布者","发布者粉丝数量","发布者是否蓝V","发布者总点赞数量","评论数", "收藏","点赞", "用户名", "评论内容", "评论时间", "评论点赞数","评论回复数", "标记"
                    reply_num = GetDouyinInfo.reply_comment(comments[j])
                    # print('回复'+str(reply_num))
                    writer.writerow(
                        [title, title_tag, publish_time, length, post, fan_num, v_tag, all_like, comment_count,
                         star,
                         like, user_name, comment_content, time_c, like_num, reply_num, tag])
                    if reply_num != 0:
                        for k in range(0, 1000):
                            # print('继续展开')
                            try:
                                reply_text = comments[j].find_element_by_css_selector("button[class='N10j3PcL']").text
                                if "展开" in reply_text:
                                    comments[j].find_element_by_css_selector("button[class='N10j3PcL']").send_keys(
                                        Keys.ENTER)
                                else:
                                    break
                            except:
                                break
                        # print('爬取回复评论')
                        replies = comments[j].find_elements_by_css_selector(
                            "div[class='nNNp3deF'] div[class='CDx534Ub']")
                        for reply in replies:
                            # 代表此条评论为楼中楼
                            tag = 0
                            # print('回复评论')
                            user_name = reply.find_element_by_css_selector(
                                "div[class='nEg6zlpW']").text
                            # 评论内容
                            comment_content = reply.find_element_by_css_selector(
                                "span[class='VD5Aa1A1']").text
                            # 评论发布时间
                            time_c = reply.find_element_by_css_selector(
                                "p[class='dn67MYhq']").text
                            # 评论点赞数
                            like_num = reply.find_element_by_css_selector(
                                "p[class='eJuDTubq']").text
                            writer.writerow(
                                [title, title_tag, publish_time, length, post, fan_num, v_tag, all_like,
                                 comment_count,
                                 star, like, user_name, comment_content, time_c, like_num, reply_num, tag])
                            # print('回复评论写入成功')
                    else:
                        # print('评论无回复')
                        continue
                k = len(comments)
                res, stop = GetDouyinInfo.douyin_slide(stop)
                if stop == 100:
                    break
                else:
                    continue

        else:
            print('无评论')
            user_name = "无评论"
            comment_content = "无评论"
            time_c = "无评论"
            like_num = "无评论"
            reply_num = "无评论"
            tag = 1
            writer.writerow(
                [title, title_tag, publish_time, length, post, fan_num, v_tag, all_like, comment_count, star, like,
                 user_name, comment_content, time_c, like_num, reply_num, tag])

    def douyin_crawl(self):
        driver.get(self.url)
        GetDouyinInfo.get_douyin_info(self.writer)


class GetKuaishouInfo:
    def __init__(self, writer1, title, post_time, post_name, photo_id):
        self.writer = writer1
        self.title = title
        self.video_post_time = post_time
        self.video_post_name = post_name
        self.id = photo_id
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Cookie': 'kpf=PC_WEB; kpn=KUAISHOU_VISION; clientid=3; did=web_1e83306028e4691a0acb7f78ecfbf145; '
                      'didv=1632459485000; client_key=65890b29; Hm_lvt_86a27b7db2c5c0ae37fee4a8a35033ee=1632459683; '
                      'userId=153866369; '
                      'kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABSkrOjzdufZa4lBYXxddWpU'
                      '-Da_CebI6GVHm2vvSBBxRUv9kJ_BKaJ3weX3FWf3acdLw2yy6uCM1MpHB8Pfi7EnJBlcRb0GqyXYMpPlaCdMqKlVo0PI'
                      '-iY9zN0wdxA89wOXtml-fWR7CFTT54hsd3PZTsTwlWBA7vhJvwim07'
                      '-A1RaTmwi66PbBkj7eCrkmJX0hdCln9MiFVyA_CL44TScBoSuDcrlwmr6APhXfdZrBO5uo0FIiA8xE'
                      '-BzwPs3Wp_Q9mI4y5GcZxo1E-B0xr4CkR4zohqJigFMAE; '
                      'kuaishou.server.web_ph=eeb2272fa742f8d8f79bd635c3e8044ac1f8 '
        }

    # w2 = GetKuaishouInfo.second_comment(self, comment_num, sub_pcursor, root_commentid)
    def second_comment(self, comment_num, w2, root_id):
        data = {
            "operationName": "visionSubCommentList",
            "variables": {
                "photoId": str(self.id),
                "rootCommentId": str(root_id),
                "pcursor": str(w2)
            },
            "query": "mutation visionSubCommentList($photoId: String, $rootCommentId: String, $pcursor: String) {\n  "
                     "visionSubCommentList(photoId: $photoId, rootCommentId: $rootCommentId, pcursor: $pcursor) {\n    "
                     "pcursor\n    subComments {\n      commentId\n      authorId\n      authorName\n      content\n      "
                     "headurl\n      timestamp\n      likedCount\n      realLikedCount\n      liked\n      status\n      "
                     "replyToUserName\n      replyTo\n      __typename\n    }\n    __typename\n  }\n}\n "

        }
        sub_comment = requests.post('https://www.kuaishou.com/graphql', headers=self.headers, json=data)
        sub_comments = json.loads(sub_comment.text)
        sub_num = len(sub_comments['data']['visionSubCommentList']['subComments'])
        for k in range(1, sub_num):
            tag = 1
            sub_name = sub_comments['data']['visionSubCommentList']['subComments'][k]['authorName']
            sub_comment = sub_comments['data']['visionSubCommentList']['subComments'][k]['content']
            sub_count = sub_comments['data']['visionSubCommentList']['subComments'][k]['likedCount']
            sub_time = sub_comments['data']['visionSubCommentList']['subComments'][k]['timestamp']
            sub_post_time = timeStamp(sub_time)
            self.writer.writerow(
                [self.title, self.video_post_name, self.video_post_name, comment_num, sub_name, sub_comment,
                 sub_post_time, sub_count, tag])
        sub_pcursor = sub_comments['data']['visionSubCommentList']['subComments'][sub_num - 1]['commentId']
        return sub_pcursor

    def first_comment(self, w1):
        data = {
            "operationName": "commentListQuery",
            "variables": {
                "photoId": str(self.id),
                "pcursor": str(w1)
            },
            "query": "query commentListQuery($photoId: String, $pcursor: String) {\n  visionCommentList(photoId: "
                     "$photoId, pcursor: $pcursor) {\n    commentCount\n    pcursor\n    rootComments {\n      "
                     "commentId\n      authorId\n      authorName\n      content\n      headurl\n      timestamp\n      "
                     "likedCount\n      realLikedCount\n      liked\n      status\n      subCommentCount\n      "
                     "subCommentsPcursor\n      subComments {\n        commentId\n        authorId\n        authorName\n  "
                     "      content\n        headurl\n        timestamp\n        likedCount\n        realLikedCount\n     "
                     "   liked\n        status\n        replyToUserName\n        replyTo\n        __typename\n      }\n   "
                     "   __typename\n    }\n    __typename\n  }\n}\n "
        }
        comment = requests.post('https://www.kuaishou.com/graphql', headers=self.headers, json=data)
        comment.encoding = 'utf-8'
        comments = json.loads(comment.text)
        comment_num = comments['data']['visionCommentList']['commentCount']
        if comment_num == 0:
            self.writer.writerow(
                [self.title, self.video_post_name, self.video_post_time, comment_num, '无评论', '无评论', '无评论', '无评论',
                 1])
            pcursor = 1
            return pcursor
        else:
            # 一级评论个数
            num = len(comments['data']['visionCommentList']['rootComments'])
            if num != 0:
                for i in range(0, num):
                    tag = 0
                    user_name = comments['data']['visionCommentList']['rootComments'][i]['authorName']
                    content = comments['data']['visionCommentList']['rootComments'][i]['content']
                    like_count = comments['data']['visionCommentList']['rootComments'][i]['likedCount']
                    root_time = comments['data']['visionCommentList']['rootComments'][i]['timestamp']
                    post_time = timeStamp(root_time)
                    self.writer.writerow(
                        [self.title, self.video_post_name, self.video_post_time, comment_num, user_name, content,
                         post_time, like_count, tag])
                    root_commentid = comments['data']['visionCommentList']['rootComments'][i]['commentId']
                    # 二级评论个数
                    sub_num = len(comments['data']['visionCommentList']['rootComments'][i]['subComments'])
                    sub_num_real = comments['data']['visionCommentList']['rootComments'][i]['subCommentCount']
                    if sub_num_real:
                        sub_comments = comments['data']['visionCommentList']['rootComments'][i]['subComments']
                        for j in range(0, sub_num):
                            tag = 1
                            sub_name = sub_comments[j]['authorName']
                            sub_content = sub_comments[j]['content']
                            sub_like = sub_comments[j]['likedCount']
                            sub_time = sub_comments[j]['timestamp']
                            sub_post_time = timeStamp(sub_time)
                            self.writer.writerow(
                                [self.title, self.video_post_name, self.video_post_time, comment_num, sub_name,
                                 sub_content, sub_post_time,
                                 sub_like, tag])
                        if sub_num < sub_num_real:
                            sub_pcursor = \
                                comments['data']['visionCommentList']['rootComments'][i]['subComments'][sub_num - 1][
                                    'commentId']
                            temp = sub_pcursor
                            w2 = ''
                            while w2 != sub_pcursor:
                                if temp == sub_pcursor:
                                    w2 = GetKuaishouInfo.second_comment(self, comment_num, sub_pcursor, root_commentid)
                                    temp = ''
                                else:
                                    sub_pcursor = w2
                                    w2 = GetKuaishouInfo.second_comment(self, comment_num, sub_pcursor, root_commentid)
                    else:
                        pass
                pcursor = comments['data']['visionCommentList']['rootComments'][num - 1]['commentId']
                if w1 == pcursor:
                    pcursor = 1
                return pcursor
            else:
                pcursor = 1
                return pcursor

    def kuaishou_crawl(self):
        w = ''
        while w != 1:
            w = GetKuaishouInfo.first_comment(self, w)


class GetBiliInfo:
    def __init__(self, title, view_number, post_name, post_time, barrage_number, view_like, view_coin,
                 view_collect, view_share, comment_number, writer, av_num):
        self.title = title
        self.view_number = view_number
        self.post_name = post_name
        self.post_time = post_time
        self.barrage_number = barrage_number
        self.view_like = view_like
        self.view_coin = view_coin
        self.view_collect = view_collect
        self.view_share = view_share
        self.comment_number = comment_number
        self.writer = writer
        self.av_num = av_num
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Cookie': "buvid3=389DFB5A-7CC1-4629-9E16-5474DFC4B674138368infoc; blackside_state=1; rpdid=|("
                      "u|kk)Ju|J)0J'uY|uJYRmJ~; LIVE_BUVID=AUTO8416071539845146; PVID=1; "
                      "buvid_fp=389DFB5A-7CC1-4629-9E16-5474DFC4B674138368infoc; "
                      "_uuid=24219D87-08A9-A277-8A0A-151A552EED9F73195infoc; sid=ifeu5z78; "
                      "fingerprint=60be89cc5c26e97768ac7b89b1f37f15; "
                      "buvid_fp_plain=3AD8F4EB-C5E8-434E-94BC-05DA3AE02A2718531infoc; CURRENT_FNVAL=976; "
                      "video_page_version=v_old_home_5; innersign=1; DedeUserID=343189276; "
                      "DedeUserID__ckMd5=8d31250d2e351de4; SESSDATA=d93730af%2C1652181766%2Cd7088*b1; "
                      "bili_jct=d2ae3fb7812242ace7d52858dec34ad6 "
        }

    def second_comment(self, temp, root_id):
        sub_comment = requests.get(
            f'https://api.bilibili.com/x/v2/reply/reply?jsonp=jsonp&pn={temp}&type=1&oid={self.av_num}&ps=10&root={root_id}',
            headers=self.headers)
        sub_comments = json.loads(sub_comment.text)
        is_end = sub_comments['data']['replies']
        if is_end:
            sub_num = len(sub_comments['data']['replies'])
            for k in range(0, sub_num):
                tag = 1
                user_name = sub_comments['data']['replies'][k]['member']['uname']
                comment = sub_comments['data']['replies'][k]['content']['message']
                post_time = sub_comments['data']['replies'][k]['ctime']
                like_count = sub_comments['data']['replies'][k]['like']
                self.writer.writerow(
                    [self.title, self.view_number, self.post_name, self.post_time, self.barrage_number, self.view_like,
                     self.view_coin, self.view_collect, self.view_share, self.comment_number, user_name, comment,
                     post_time, like_count, tag])
            temp += 1
            return temp
        else:
            return -1

    def first_comment(self, w1):
        comment = requests.get(
            f'https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={w1}&type=1&oid={self.av_num}&mode=3&plat=1',
            headers=self.headers)
        comment.encoding = 'utf-8-sig'
        comments = json.loads(comment.text)
        is_end = comments['data']['cursor']['is_end']
        if is_end:
            return 1
        else:
            # 一级评论个数
            num = len(comments['data']['replies'])
            if num != 0:
                for i in range(0, num):
                    tag = 0
                    user_name = comments['data']['replies'][i]['member']['uname']
                    comment = comments['data']['replies'][i]['content']['message']
                    post_time = comments['data']['replies'][i]['ctime']
                    like_count = comments['data']['replies'][i]['like']
                    self.writer.writerow(
                        [self.title, self.view_number, self.post_name, self.post_time, self.barrage_number,
                         self.view_like, self.view_coin, self.view_collect, self.view_share, self.comment_number,
                         user_name, comment, post_time, like_count, tag])
                    root_comment_id = comments['data']['replies'][i]['rpid']
                    # 二级评论个数
                    sub_num_real = comments['data']['replies'][i]['replies']
                    if sub_num_real:
                        pn = 1
                        while pn != -1:
                            pn = GetBiliInfo.second_comment(self, pn, root_comment_id)
                            # temp += 1
                    else:
                        continue
                next_w = comments['data']['cursor']['next']
                return next_w
            else:
                return 1

    def bili_crawl(self):
        w = 0
        while w != 1:
            w = GetBiliInfo.first_comment(self, w)
            time.sleep(3)
            # print('w' + str(w))


class GetWeiboInfo:
    # def __init__(self, writer1, title1, publisher1, transmit_count1, comment_count1, like_count1, length, play_number,
    #              text2, weibo_tag, id1):
    def __init__(self, writer1, publisher1,location1,fan_number1, transmit_count1, comment_count1, like_count1,
                 text2, weibo_tag, id1, sim1):
        self.writer = writer1
        #self.title = title1
        self.publisher = publisher1
        self.transmit_count = transmit_count1
        self.comment_count = comment_count1
        self.like_count = like_count1
        #self.len = length
        #self.play_num = play_number
        self.text = text2
        self.fan_number=fan_number1
        self.loc = location1
        self.wtag = weibo_tag
        self.id = id1
        self.sim = sim1
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.101 Safari/537.36',
            'Cookie': 'SINAGLOBAL=2091729837087.3728.1661664246202; UOR=,,login.sina.com.cn; XSRF-TOKEN=9cy-hdaSldlPBhk8N9dPNo4v; SSOLoginState=1662793242; _s_tentry=weibo.com; Apache=9202328576743.148.1662793253762; ULV=1662793253807:10:5:2:9202328576743.148.1662793253762:1662278254307; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5Lr7ToH0NN_3s3_hzAsuhz5JpX5KMhUgL.FoMfSoBX1K-pe0n2dJLoIEyuIg_ai--NiKnRi-zpi--fiKnpiKLWi--Xi-i2iKLhi--Xi-zRiKLW; ALF=1694415715; SCF=Amps_M75cltwDa7Bm_lemms_kl0xDiagRUKtvtZqGgW6WNxeESW5ES1ufOTvUm3f2LzojE5PPF1njc3WePGDlZc.; SUB=_2A25OGfezDeRhGeFL7VYV-SvNyDSIHXVtb257rDV8PUNbmtAKLRjFkW9NfcyWNj9SBew44xJfg6w0UX1HmqagYrAy; WBPSESS=5g_hz7cPq45HfXaHdb9Wl6SPRm-0FeswQvjkL6s4XgmDmjLb1CMnMJdsrhYvUOFL1XBz0L2zT3_MI2GMesFODxW8Z4CQwVBBllKHPf-VdLRtXhN44idYX_e61yXbyzyJsuwANVj2Yv70bVG8GS9tCA==',
            'Connection' : 'close'
        }

    def second_comment(self, temp, w2, root_id,follow_count1):
        if temp == 0:
            sub_comment = requests.get(
                f'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={root_id}&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id={w2}&count=20',
                headers=self.headers)
        else:
            sub_comment = requests.get(
                f'https://weibo.com/ajax/statuses/buildComments?flow={temp}&is_reload=1&id={root_id}&is_show_bulletin=2&is_mix=1&fetch_level=1&max_id={w2}&count=20',
                headers=self.headers)
        sub_comments = json.loads(sub_comment.text)
        sub_num = len(sub_comments['data'])
        for k in range(0, sub_num):
            tag = 1
            user_name = sub_comments['data'][k]['user']['screen_name']
            comment = sub_comments['data'][k]['text_raw']
            post_time = sub_comments['data'][k]['created_at']
            c_post_time = gmt_trans(post_time)
            like_count = sub_comments['data'][k]['like_counts']
            try:
                loc2 = sub_comments['data'][k]['user']['location']
                loc2 = loc2.split(" ")[0]
                #print(loc2)
            except IndexError:
                loc2=None


            # self.writer.writerow(
            #     [self.title, self.publisher, self.comment_count, self.transmit_count, self.like_count, self.len,
            #      self.play_num, self.text, self.wtag, user_name, comment, c_post_time, like_count, tag])
            self.writer.writerow(
                [self.publisher,self.loc,self.fan_number, self.transmit_count, self.comment_count,  self.like_count,
                 self.text, self.wtag,follow_count1,user_name,loc2,comment, c_post_time, like_count, self.sim, tag])
        sub_max_id = sub_comments['max_id']
        return sub_max_id

    def first_comment(self, w1):
        comment = requests.get(
            f'https://weibo.com/ajax/statuses/buildComments?flow=0&is_reload=1&id={self.id}&is_show_bulletin=2&is_mix=0&max_id={w1}&count=20',
            headers=self.headers)
        comment.encoding = 'utf-8-sig'
        # try:
        comments = json.loads(comment.text)
        # 一级评论个数
        num = len(comments['data'])
        if num != 0:
            for i in range(0, num):
                tag = 0
                user_name = comments['data'][i]['user']['screen_name']
                comment = comments['data'][i]['text_raw']
                post_time = comments['data'][i]['created_at']
                c_post_time = gmt_trans(post_time)
                like_count = comments['data'][i]['like_counts']
                follow_count=comments['data'][i]['user']['followers_count']
                try:
                    loc2=comments['data'][i]['user']['location']
                    loc2 = loc2.split(" ")[0]
                    #print(loc2)
                except IndexError:
                    loc2 = None


                # self.writer.writerow(
                #     [self.title, self.publisher, self.comment_count, self.transmit_count, self.like_count, self.len,
                #      self.play_num, self.text, self.wtag, user_name, comment, c_post_time, like_count, tag])
                self.writer.writerow(
                    [self.publisher,self.loc,self.fan_number,self.transmit_count, self.comment_count,  self.like_count,
                     self.text, self.wtag, follow_count, user_name,loc2,comment, c_post_time, like_count, self.sim, tag])
                root_comment_id = comments['data'][i]['id']
                # 二级评论个数
                sub_num_real = comments['data'][i]['total_number']
                if sub_num_real:
                    sub_max_id = 0
                    temp = sub_max_id
                    w2 = 1
                    while w2 != 0:
                        if temp == 0:
                            w2 = GetWeiboInfo.second_comment(self, temp, sub_max_id, root_comment_id,follow_count)
                            temp += 1
                        else:
                            sub_max_id = w2
                            w2 = GetWeiboInfo.second_comment(self, temp, sub_max_id, root_comment_id,follow_count)
                else:
                    continue
            max_id = comments['max_id']
            if max_id == 0:
                max_id = 1
            return max_id
        else:
            max_id = 1
            return max_id

    def weibo_craw(self):
        w = 0
        while w != 1:
            time.sleep(3)
            w = GetWeiboInfo.first_comment(self, w)
        print('爬虫完成')


def kuaishou(writer, url1):
    driver.get(url1)
    time.sleep(2)
    # 标题
    title = driver.find_element_by_xpath("//p[@class='video-info-title']").text
    while title == '':
        print('请检查网页状态')
        driver.implicitly_wait(10)
        title = driver.find_element_by_xpath("//p[@class='video-info-title']").text
    # 发布者
    post_name = driver.find_element_by_xpath("//span[@class='profile-user-name-title']").text
    # 发布时间
    post_time = driver.find_element_by_xpath("//span[@class='photo-time']").text
    photo_id = re.findall(r'short-video/(.+)', url1)
    photo_id = ''.join(photo_id)
    getinfo = GetKuaishouInfo(writer, title, post_name, post_time, photo_id)
    getinfo.kuaishou_crawl()


def weibo(writer, url1, num1,key):
    if num1 != 2:
        try:
            driver.get(url1)
            driver.implicitly_wait(10)  # 10秒内找到元素就开始执行
            # 视频标题
            #title = driver.find_element(By.XPATH, "//div[@class='Detail_tith3_2pyML']").text
            #driver.implicitly_wait(10)

            # 发布者
            #publisher = driver.find_element(By.XPATH, "//div[@class='star-autocut star-f16']").text
            publisher = driver.find_element(By.XPATH, "//div[@class='woo-box-flex woo-box-alignCenter head_nick_1yix2']").text
            #//div[@class='woo-box-flex woo-box-alignCenter head_nick_1yix2']

            # 博客转发数量
            #transmit = driver.find_element(By.XPATH,
                                    #"//div[@class='woo-box-flex woo-box-alignCenter Detail_opt_2w8oi'][1]").text
            transmit = driver.find_element(By.XPATH,
                                           "//div[@class='woo-box-flex woo-box-alignCenter woo-box-justifyCenter toolbar_wrap_np6Ug']/span[@class='toolbar_num_JXZul']").text
            #//div[@class='woo-box-flex woo-box-alignCenter woo-box-justifyCenter toolbar_wrap_np6Ug']/span[@class='toolbar_num_JXZul']
            res1 = re.findall(r'\d', transmit)
            transmit_count = ''.join(res1)
            if transmit_count == '':
                transmit_count = 0

            # 博客评论数
            # comment = driver.find_element(By.XPATH,
            #                               "//div[@class='woo-box-flex woo-box-alignCenter Detail_opt_2w8oi'][2]").text
            comment = driver.find_element(By.XPATH,
                                          "//div[@class='woo-box-flex woo-box-alignCenter woo-box-justifyCenter toolbar_wrap_np6Ug toolbar_cur_JoD5A']/span[@class='toolbar_num_JXZul']").text
            #//div[@class='woo-box-flex woo-box-alignCenter woo-box-justifyCenter toolbar_wrap_np6Ug toolbar_cur_JoD5A']/span[@class='toolbar_num_JXZul']
            res2 = re.findall(r'\d', comment)
            comment_count = ''.join(res2)
            if comment_count == '':
                comment_count = 0

            # 博客点赞数量
            # like = driver.find_element(By.XPATH,
            #                            "//div[@class='woo-box-flex woo-box-alignCenter Detail_opt_2w8oi'][3]").text
            like = driver.find_element(By.XPATH,
                                       "//span[@class='woo-like-count']").text
            #//span[@class='woo-like-count']
            res3 = re.findall(r'\d', like)
            like_count = ''.join(res3)
            if like_count == '':
                like_count = 0

            # text
            #text2 = driver.find_element(By.XPATH, "//div[@class='woo-box-item-flex Txt_cut_1Pb86']").text
            text2 = driver.find_element(By.XPATH, "//div[@class='detail_wbtext_4CRf9']").text
            t = re.findall('[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u4e00-\u9fa5]',
                           text2)
            #t = re.findall(r'[^\*"/:?\\|<>【】&¥%*@]', t, re.S)
            t = ''.join(t)
            #print(t)

            #//div[@class='detail_wbtext_4CRf9']

            # tag
            weibo_tag = []
            #tags = driver.find_elements(By.XPATH, "//div[@class='woo-box-item-flex Txt_cut_1Pb86']//a")
            tags = driver.find_elements(By.XPATH, "//div[@class='detail_wbtext_4CRf9']/a")
            #//div[@class='detail_wbtext_4CRf9']/a
            for tag in tags:
                weibo_tag.append(tag.text)
            weibo_tag = ''.join(weibo_tag)

            # length
            # length = driver.find_element(By.XPATH, "//span[@class='wbpv-duration-display']").get_attribute(
            #     'textContent')
            # while length == '':
            #     time.sleep(1)
            #     length = driver.find_element(By.XPATH, "//span[@class='wbpv-duration-display']").get_attribute(
            #         'textContent')

            # # # 播放次数
            # play_num = driver.find_element(By.XPATH, "//div[@class='star-f16']").text
            # res = re.findall(r'(.+?)次', play_num)
            # text1 = ''.join(res)
            # if '万' in text1:
            #     num = re.findall(r'(.+?)万', text1)
            #     data1 = ''.join(num)
            #     if '.' in data1:
            #         number = float(data1) * 10000
            #     else:
            #         data1 = re.findall(r'\d+', text1)
            #         data1 = ''.join(data1)
            #         number = float(data1) * 10000
            #     play_number = int(number)
            # else:
            #     data = re.findall(r'\d+', text1)
            #     data1 = ''.join(data)
            #     play_number = int(float(data1))

            #帖子账号粉丝数
            fans = driver.find_element(By.XPATH, "//div[@class='f14 cla']/div").text
            #print(fans)
            # play_num = driver.find_element(By.XPATH, "//div[@class='star-f16']").text
            # res = re.findall(r'(.+?)次',video_id)
            text1 = ''.join(fans)
            if '万' in text1:
                num = re.findall(r'(.+?)万', text1)
                data1 = ''.join(num)
                if '.' in data1:
                    number = float(data1) * 10000
                else:
                    data1 = re.findall(r'\d+', text1)
                    data1 = ''.join(data1)
                    number = float(data1) * 10000
                fan_number = int(number)
            else:
                data = re.findall(r'\d+', text1)
                data1 = ''.join(data)
                fan_number = int(float(data1))

            #发布者ip地址
            #//div[@class='head-info_ip_3ywCW']
            try:
                location = driver.find_element(By.XPATH, "//div[@class='head-info_ip_3ywCW']").text
                loc = location.split(" ")[1]
                #print(loc)
            except IndexError:
                loc=None
                #print(loc)


            if comment_count != 0:
                # video_id = driver.find_element(By.XPATH,
                #                                "//div[@class='Scroll_container_1_-C6 Comments_mar1_xaWeE']").get_attribute(
                #     'id')

                #计算主题相似度
                lda_sim = lda_news.cal_query_doc_similarity(query=key, document=t)
                print("主题相似度为：", lda_sim)

                video_id = driver.find_element(By.XPATH, "//a[@class='head-info_time_6sFQg']").get_attribute('href').split('/')[4]
                video_id = url_to_mid(video_id)
                # getinfo = GetWeiboInfo(writer, title, publisher, transmit_count, comment_count, like_count, length,
                #                        play_number, text2, weibo_tag, video_id)
                getinfo = GetWeiboInfo(writer, publisher,loc,fan_number, transmit_count, comment_count, like_count,
                                         t, weibo_tag, video_id,lda_sim)
                getinfo.weibo_craw()


            # else:
            #     writer.writerow(
            #         # [title, publisher, transmit_count, comment_count, like_count, length, play_number, text2, weibo_tag,
            #         #  '无评论',
            #         #  '无评论', '无评论', '无评论', 0])
            #         [ publisher,fan_number, transmit_count, comment_count, like_count, text2, weibo_tag,
            #          '无评论',
            #          '无评论', '无评论', '无评论', 0])
        except (Exception, BaseException) as e:
            print(e)
            num1 += 1
            weibo(writer, url1, num1,key)
    else:
        return False


def bilibili(writer, url1):
    driver.get(url1)
    av_number = bv2av(url1)
    # title
    title = driver.find_element_by_xpath("//h1").get_attribute('title')
    # 视频播放量
    view = driver.find_element_by_xpath("//span[@class='view']").text
    view_number1 = re.findall(r'\d', view)
    view_number = ''.join(view_number1)
    # 发布者
    post_name = driver.find_element_by_css_selector("div.name>a:nth-child(1)").text
    # 发布时间
    post_time = driver.find_element_by_xpath("//div[@class='video-data']/span[3]").text
    # 弹幕数量
    barrage = driver.find_element_by_xpath("//span[@class='dm']").text
    res = re.findall(r'\d', barrage)
    barrage_number = ''.join(res)
    # 视频点赞数
    view_like1 = driver.find_element_by_xpath("//span[@class='like']").text
    res = re.findall(r'\d', view_like1)
    if res:
        view_like = ''.join(res)
    else:
        view_like = 0
    # 视频投币
    view_coin1 = driver.find_element_by_xpath("//span[@class='coin']").text
    res = re.findall(r'\d', view_coin1)
    if res:
        view_coin = ''.join(res)
    else:
        view_coin = 0
    # 视频收藏
    view_collect1 = driver.find_element_by_xpath("//span[@class='collect']").text
    res = re.findall(r'\d', view_collect1)
    if res:
        view_collect = ''.join(res)
    else:
        view_collect = 0
    # 视频分享
    view_share1 = driver.find_element_by_xpath("//span[@class='share']").text
    res = re.findall(r'\d', view_share1)
    if res:
        view_share = ''.join(res)
    else:
        view_share = 0
    # 评论数量
    comment_number = driver.find_element_by_xpath("//span[@class='b-head-t results']").text
    if comment_number != '0':
        getinfo = GetBiliInfo(title, view_number, post_name, post_time, barrage_number, view_like, view_coin,
                              view_collect, view_share, comment_number, writer, av_number)
        getinfo.bili_crawl()
    else:
        writer.writerow(
            [title, view_number, post_name, post_time, barrage_number, view_like, view_coin, view_collect, view_share,
             comment_number, "无评论", "无评论", "无评论", "无评论", "无评论"])


def begin_solo(web, key, url1):
    websites = ['douyin', 'kuaishou', 'bili', 'weibo']
    file = websites[web - 1] + key + '数据.csv'
    if web == 1:
        with open(file, "a+", errors="ignore", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            getinfo = GetDouyinInfo(writer, url1)
            writer.writerow(
                ["标题", "标题tag", "发布时间", "视频时长", "发布者", "发布者粉丝数量", "发布者是否蓝V", "发布者总点赞数量", "评论数", "收藏", "点赞", "用户名",
                 "评论内容", "评论时间", "评论点赞数", "评论回复数", "标记"])
            douyin_signin(url1)
            getinfo.douyin_crawl()
    elif web == 2:
        with open(file, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(["标题", "发布者", "发布时间", "评论数", "用户名", "评论内容", "评论点赞数", "评论发表时间"])
            kuaishou(writer, url1)
    elif web == 3:
        with open(file, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(
                ["标题", "发布者", "发布时间", "视频播放量", "弹幕数量", "视频点赞", "视频投币", "视频收藏", "视频分享", "评论数", "用户名", "评论内容", "评论时间",
                 "评论点赞数", "标记"])
            bilibili(writer, url1)
    elif web == 4:
        with open(file, "a+", errors="ignore", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            #writer.writerow(["标题", "发布者", "评论数", "转发数", "点赞数", "用户名", "评论内容", "评论时间", "评论点赞数", "标记"])
            writer.writerow(["发布者","帖子账号粉丝数", "转发数", "评论数", "点赞数", "一级账号粉丝数","用户名", "评论内容", "评论时间", "评论点赞数", "主题相似度" ,"标记"])
            weibo(writer, url1, 0,key)


def begin_file(web, key, file2):
    websites = ['douyin', 'kuaishou', 'bili', 'weibo']
    file3 = websites[web - 1] + key + '数据.csv'
    if 'csv' in file2:
        cluster = pd.read_csv(file2, encoding='utf-8', sep=';')
    elif 'xlsx' in file2:
        cluster = pd.read_excel(file2)
    elif 'txt' in file2:
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
    if web == 1:
        with open(file3, "a+", errors="ignore", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(
                ["标题", "标题tag", "发布时间", "视频时长", "发布者", "发布者粉丝数量", "发布者是否蓝V", "发布者总点赞数量", "评论数", "收藏", "点赞", "用户名",
                 "评论内容", "评论时间", "评论点赞数", "评论回复数", "标记"])
            rows = len(sheet)
            # douyin_signin(sheet[0])
            for i in range(0, rows):
                url1 = sheet[i]
                getinfo = GetDouyinInfo(writer, url1)
                getinfo.douyin_crawl()
                view_bar(i, rows)
    elif web == 2:
        with open(file3, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(["标题", "发布者", "发布时间", "评论数", "用户名", "评论内容", "评论点赞数", "评论发表时间"])
            rows = len(sheet)
            for i in range(0, rows):
                url2 = sheet[i]
                time.sleep(3)
                kuaishou(writer, url2)
                view_bar(i, rows)
    elif web == 3:
        with open(file3, "a+", errors="ignore", newline='', encoding='utf-8') as fp:
            writer = csv.writer(fp, delimiter=';')
            writer.writerow(
                ["标题", "发布者", "发布时间", "视频播放量", "弹幕数量", "视频点赞", "视频投币", "视频收藏", "视频分享", "评论数", "用户名", "评论内容", "评论时间",
                 "评论点赞数", "标记"])
            rows = len(sheet)
            for i in range(0, rows):
                url3 = sheet[i]
                time.sleep(3)
                bilibili(writer, url3)
                view_bar(i, rows)
    elif web == 4:
        with open(file3, "a+", errors="ignore", newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            # writer.writerow(
            #     ["标题", "发布者", "评论数", "转发数", "点赞数", "视频长度", "播放量", "文本", "话题", "用户名", "评论内容", "评论时间", "评论点赞数", "标记"])
            writer.writerow(
                ["发布者","IP属地","帖子账号粉丝数", "转发数", "评论数", "点赞数", "文本", "话题", "一级账号粉丝数","用户名","评论属地", "评论内容", "评论时间", "评论点赞数", "主题相似度" ,"标记"])
            rows = len(sheet)
            for i in range(0, rows):
                url4 = sheet[i]
                print(url4)
                weibo(writer, url4, 0,key)
                time.sleep(10)
                view_bar(i, rows)
        print("\n数据爬取结束，原始数据保存为：{}".format(file3))
        driver.close()

    cleandata(file3)

    # cluster.close()

def cleandata(file_name):
    print('---------------------------------------------------------------')
    print("根据主题相似度过滤信息开始")
    data = pd.read_csv(file_name, encoding='utf-8', sep=';')
    sim = data['主题相似度']
    Max = float(max(sim))
    Min = float(min(sim))

    for i in range(0, len(sim)):
        #print(sim[i])
        m = (float(sim[i]) - Min) / (Max - Min)
        #print(m)
        if m <= 0.1:
             # 删除整行数据
            data = data.drop(i, axis=0)  # 注意：drop() 方法不改变原有的 df 数据！
        #sim[i] = m
    # 保存新的csv文件
    data.to_csv("clean-" + file_name, index=False, encoding="utf-8", sep=';')
    print("信息过滤完成,数据保存为：{}".format("clean-" + file_name))



# input_keyword = input('请输入爬虫关键词：')
# website = input('请输入待爬虫网站(抖音1快手2B站3微博4)：')
# type_url = input('单个链接输入1，csv或xlsx或txt文件输入2：')
# if type_url == '1':
#     url = input('请输入链接：')
#     begin_solo(int(website), input_keyword, url)
# elif type_url == '2':
#     file = input('请输入文件路径：')
#     begin_file(int(website), input_keyword, file)
#driver.close()
