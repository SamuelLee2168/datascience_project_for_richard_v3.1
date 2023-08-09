import pandas as pd
import numpy as np
import streamlit as st
import datetime
import random
import plotly_express as px
from datetime import datetime, timedelta

stock_basic = pd.read_csv("data/stock_basic.csv")

def split_by_market(df):
    market_1 = df.loc[df['大盘']=="主板"]
    market_2 = df.loc[df['大盘']=="科创板"]
    market_3 = df.loc[df['大盘']=="创业板"]
    market_4 = df.loc[df['大盘']=="北交所"]
    return market_1,market_2,market_3,market_4

def display_table(df,head,font_size):
    # CSS to inject contained in a string
    hide_table_row_index = """
                <style>
                thead tr th:first-child {display:none}
                tbody th {display:none}
                </style>
                """

    # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    # Display a static table
    st.table(df.head(head))
    
    st.markdown(
        """
        <style>
        table {
            font-size: """+str(font_size)+"""px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def display_data(df,expander_name,head,font_size,start_date,end_date,top_x):
    with st.expander(expander_name):
        st.text('以下的对比表格用强势系数的列表来排序，显示了强势系数最高的'+str(top_x)+'个股票')
        display_table(df,head,font_size)
        

        st.text("以下的图里每条线代表一个股票，上方对比表格里的股票都在下方的图标里面。X轴是日期，Y轴是强势系数。")
        st.text("鼠标悬浮在图里的某个点的时候可以看到那个位置的具体时间和强势系数。")
        st.text("右侧显示着每支股票对应的颜色。点击右侧的股票名称可以在图中隐藏或显示那支股票。")
        #daily = generate_daily_of_several_stocks(df,head,str(start_date),str(end_date))
        #px_plot = px.line(daily,x="日期",y=daily.columns.drop("日期"),labels={"value":"强势系数"})
        #st.plotly_chart(px_plot)
    

def get_rating_for_time_period_of_stock(stock_code,start_time,end_time,file_path):
    df = pd.read_csv(file_path+stock_code+".csv")
    df_in_time_frame = df.loc[df['date']>=start_time]
    df_in_time_frame = df_in_time_frame.loc[df['date']<=end_time]
    if df_in_time_frame.shape[0]>0:
        return np.average(df_in_time_frame['rating'])
    else:
        return 0

def get_B1_B2_of_all_stocks_in_time_period(rating_name):
    if rating_name == "强势系数B1":
        file_path = "data/B1_ratings/"
    else:
        file_path = "data/B2_ratings/"
    stock_ratings_in_time_period = []
    for stock_code in stock_basic['ts_code']:
        stock_ratings_in_time_period.append(get_rating_for_time_period_of_stock(stock_code,start_time,end_time,file_path))
    return pd.DataFrame({"股票名称":stock_basic['name'],"大盘":stock_basic['market'],"行业":stock_basic['industry'],rating_name:stock_ratings_in_time_period}).sort_values(rating_name,ascending=False)

#-------------------------------------------------


st.title("股票强势系数分析-V3")
st.header("输入参数")

start_time = int(st.text_input("以下输入开始计算强势系数的时间。格式是YYYYMMDD",value="20220915"))
end_time = int(st.text_input("以下输入停止计算强势系数的时间",value="20230323"))
top_rows_displayed = int(st.text_input("计算出结果后因该显示多少个强势系数最高的股票",value=10))
#b1_ma_days = int(st.text_input("B1使用的均线天数（可参考B1公式）",value=5))
#b2_ma_days = int(st.text_input("B2使用的均线天数（可参考B2公式）",value=5))
#b3_time_segment = int(st.text_input("B3涨速时段时长（可参考B3定义文档）",value=5))
#b4_time_segment = int(st.text_input("B4涨速时段时长（可参考B4定义文档）",value=5))
#b3_top_segment_count = int(st.text_input("B3相对涨速最靠前的数量（可参考B3定义文档）",value=3))
#b4_top_segment_count = int(st.text_input("B4相对涨速最靠前的数量（可参考B4定义文档）",value=3))
#b3_index_scale_factor = int(st.text_input("B3板块涨速放大因子（可参考B3定义文档）",value=1))
#b4_index_scale_factor = int(st.text_input("B4大盘涨速放大因子（可参考B4定义文档）",value=1))

with st.spinner("正在计算强势系数。。。"):
    b1_ratings = get_B1_B2_of_all_stocks_in_time_period("强势系数B1")
    b2_ratings = get_B1_B2_of_all_stocks_in_time_period("强势系数B2")
    b2_market_1,b2_market_2,b2_market_3,b2_market_4 = split_by_market(b2_ratings)



st.header("计算结果")
display_data(b1_ratings,"根据强势系数B1排序的股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
display_data(b2_ratings,"根据强势系数B2排序的股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
display_data(b2_market_1,"根据强势系数B2排序的主板股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
display_data(b2_market_2,"根据强势系数B2排序的科创板股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
display_data(b2_market_3,"根据强势系数B2排序的创业板股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
display_data(b2_market_4,"根据强势系数B2排序的北交所股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
#display_data(b3_ratings,"根据强势系数B3排序的股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
#display_data(b4_ratings,"根据强势系数B4排序的股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
#display_data(b4_market_1,"根据强势系数B4排序的主板股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
#display_data(b4_market_2,"根据强势系数B4排序的科创板股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
#display_data(b4_market_3,"根据强势系数B4排序的创业板股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)
#display_data(b4_market_4,"根据强势系数B4排序的北交所股票",top_rows_displayed,1,start_time,end_time,top_rows_displayed)