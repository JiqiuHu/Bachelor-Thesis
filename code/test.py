import streamlit as st
import pandas as pd
from pyecharts.charts import Bar
from pyecharts.charts import Map
from pyecharts.faker import Faker
import streamlit_echarts
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from streamlit_echarts import st_echarts
from streamlit_echarts import st_pyecharts
from streamlit.components.v1 import html
import main
import 画图

# uploaded_file = st.file_uploader("Upload your data here")
# if uploaded_file is not None:
#     st.success('upload success!')
#     main.emotion_analysis(uploaded_file.name)
# else:
#     st.error('upload failed!')
# side_bar = st.sidebar.radio(
#     '数据情感分析结果：',
#     ['群体情绪排行榜', '群体情绪中国地图', '集群密度排行', '点赞评论转发占比图', '群体情绪趋势图']
# )
def analysis(side_bar,uploaded_file):
    if side_bar == '群体情绪排行榜':
        title_P, emotion_P, title_N, emotion_N = 画图.read_data()
        col1, col2, col3 = st.columns([1, 0.2, 0.2])
        with col1:
            st.write('群体情绪节目排行')
        with col2:
            sp = st.button('正向')
        with col3:
            sn = st.button('负向')
        if sp:
            option = {'grid': {'top': 10, 'left': 300, 'right': 10, 'bottom': 50},
                      'tooltip': {'trigger': 'axis', 'confine': 'true'},
                      'yAxis': {'triggerEvent': 'true', 'data': title_P},
                      'xAxis': {},
                      'series': [{'name': '群体正向情绪', 'type': 'bar', 'data': emotion_P, 'itemStyle': {'normal':
                                  {'label': {
                                      'show': 'true',
                                      'position': 'right',
                                      'textStyle': {
                                          'color': 'black'}}}}}]}
            st_echarts(options=option, height='500px', width='700px')
            with st.expander('展开显示全部标题'):
                lp = len(title_P)
                for i in range(0, lp):
                    st.write(str(i) + ': ' + title_P[lp - i - 1])
        if sn:
            option = {'grid': {'top': 48, 'left': 300, 'right': 15, 'bottom': 50},
                      'tooltip': {'trigger': 'axis', 'confine': 'true'},
                      'yAxis': {'triggerEvent': 'true', 'data': title_N, 'inverse': 'true'},
                      'xAxis': {'inverse': 'true'},
                      'series': [{'name': '群体负向情绪', 'type': 'bar', 'data': emotion_N, 'itemStyle': {'normal':
                                  {'label': {
                                      'show': 'true',
                                      'position': 'right',
                                      'textStyle': {
                                          'color': 'black'}}}}}]}
            st_echarts(options=option, height='500px', width='700px')
            with st.expander('展开显示全部标题'):
                ln = len(title_N)
                for j in range(0, ln):
                    st.write(str(j) + ': ' + title_N[j])
    if side_bar == '群体情绪中国地图':
        dic = 画图.emotion_map(uploaded_file.name)
        c = Map(init_opts=opts.InitOpts(bg_color="white"))
        c.add("群体情绪中国地图", [list(z) for z in zip(dic.keys(), dic.values())], maptype="china")
        c.set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        c.set_global_opts(
            title_opts=opts.TitleOpts(title="China"),
            visualmap_opts=opts.VisualMapOpts(max_=1, min_=-1, range_color=["#B40404", "#FFFFFF", "#31B404"])
        )
        text = c.render_embed()
        html(text, height=700, width=800)
    if side_bar == '集群密度排行':
        title_D, density = 画图.cluster_density()
        c1, c2 = st.columns([1, 0.3])
        with c1:
            st.write('集群密度排行榜')
        with c2:
            st.empty()
        option = {'grid': {'top': 48, 'left': 300, 'right': 10, 'bottom': 50},
                  'tooltip': {'trigger': 'axis', 'confine': 'true'},
                  'yAxis': {'triggerEvent': 'true', 'data': title_D,
                            'axisLabel': {'show': 'true'}},
                  'xAxis': {},
                  'series': [{'name': '集群密度', 'type': 'bar', 'data': density,
                              'itemStyle': {'normal': {'label': {'show': 'true', 'position': 'right',
                                                                 'textStyle': {'color': 'black'}}}}}]}

        st_echarts(options=option, height='700px', width='700px')
        with st.expander('展开显示全部标题'):
            ld = len(title_D)
            for i in range(0, ld):
                st.write(str(i) + ': ' + title_D[ld - i - 1])
    if side_bar == '点赞评论转发占比图':
        p_p, p_n = 画图.emotion_pie(uploaded_file.name)
        b1, b2, b3 = st.columns([1, 0.3, 0.3])
        with b1:
            st.empty()
        with b2:
            pp = st.button('正面')
        with b3:
            pn = st.button('负面')
        if pp:
            option1 = {'title': {'text': '正面情绪点赞评论转发占比图', 'x': 'center'},
                       'tooltip': {'trigger': 'item', 'formatter': "{a} <br/>{b} : {c} ({d}%)"},
                       'legend': {'orient': 'vertical', 'left': 'left', 'data': ['评论', '转发', '点赞']},
                       'series': [{'name': '访问来源', 'type': 'pie', 'radius': '55%',
                                   'label': {'show': 'true', 'formatter': '{b} : {c} ({d}%)'},
                                   'labelLine': {'show': 'true'},
                                   'data': [{'value': int(p_p["评论"]), 'name': '评论'},
                                            {'value': int(p_p["转发"]), 'name': '转发'},
                                            {'value': int(p_p["点赞"]), 'name': '点赞'}]}]}
            st_echarts(options=option1, height='500px')
        if pn:
            option2 = {'title': {'text': '负面情绪点赞评论转发占比图', 'x': 'center'},
                       'tooltip': {'trigger': 'item', 'formatter': "{a} <br/>{b} : {c} ({d}%)"},
                       'legend': {'orient': 'vertical', 'left': 'left', 'data': ['评论', '转发', '点赞']},
                       'series': [{'name': '访问来源', 'type': 'pie', 'radius': '55%',
                                   'label': {'show': 'true', 'formatter': '{b} : {c} ({d}%)'},
                                   'labelLine': {'show': 'true'},
                                   'data': [{'value': int(p_n["评论"]), 'name': '评论'},
                                            {'value': int(p_n["转发"]), 'name': '转发'},
                                            {'value': int(p_n["点赞"]), 'name': '点赞'}]}]}
            st_echarts(options=option2, height='500px')
    if side_bar == '群体情绪趋势图':
        dp, dz, dn = 画图.emotion_tendency(uploaded_file.name)
        option = {'title': {'text': '群体情绪趋势图'},
                  'legend': {'data': ['正面', '中性', '负面']},
                  'xAxis': {'type': 'category', 'data': [list(z) for z in zip(dp.keys())], 'axisLabel': {'interval': 0}},
                  'yAxis': {'type': 'value'},
                  # 提示框，鼠标悬浮交互时的信息提示
                  'tooltip': {'show': 'true',  # 是否显示
                              'trigger': 'axis',  # 触发类型，默认数据触发，见下图，可选为：'item' | 'axis'
                              },
                  'dataZoom': {'type': 'slider', 'xAxisIndex': [0], 'show': 'true', 'height': 20, 'bottom': 0,
                               'zoomLock': 'true', 'minValueSpan': 0, 'maxValueSpan': 7, 'realtime': 'true',
                               'showDetail': 'false', 'filterMode': 'empty'},
                  # 指定图标的类型
                  'series': [  # 第一条折线图
                      {'name': '正面', 'type': 'line', 'data': list(dp.values())},
                      # 第二条折线图
                      {'name': '中性', 'type': 'line', 'data': list(dz.values())},
                      {'name': '负面', 'type': 'line', 'data': list(dn.values())}]}
        st_echarts(options=option, height='500px')

    # if sn:
