import pandas as pd
import numpy as np
import streamlit as st
import datetime
import random
import plotly_express as px
from datetime import datetime, timedelta
import os

stock_basic = pd.read_csv("data/stock_basic.csv")



#-----------------------
@st.cache_data(show_spinner=False)
def get_data_of_rating(file_path):
    return pd.read_csv(file_path)

@st.cache_data(show_spinner=False)
def combine_rating_data(file_path):
    dfs = []
    for file_name in os.listdir(file_path):
        dfs.append(pd.read_csv(file_path+file_name))
    return pd.concat(dfs)

all_b1_rating_data = combine_rating_data("data/B1_ratings/")
all_b2_rating_data = combine_rating_data("data/B2_ratings/")
all_b3_rating_data = combine_rating_data("data/B3_ratings/")
all_b4_rating_data = combine_rating_data("data/B4_ratings/")
print(f"b3 len is {all_b3_rating_data.shape[0]}")
print(f"b4 len is {all_b4_rating_data.shape[0]}")

#------------------------

def split_by_market(df):
    market_1 = df.loc[df['大盘']=="主板"]
    market_2 = df.loc[df['大盘']=="科创板"]
    market_3 = df.loc[df['大盘']=="创业板"]
    market_4 = df.loc[df['大盘']=="北交所"]
    return market_1,market_2,market_3,market_4

def display_table(df):
    st.dataframe(df, hide_index=True)
    
def int_to_timestamp(int):
    return pd.to_datetime(int, format='%Y%m%d')

def get_df_for_plotting(stock_names,start_time,end_time,rating_name):
    if rating_name == "强势系数B1":
        total_rating_df = all_b1_rating_data
    elif rating_name == "强势系数B2":
        total_rating_df = all_b2_rating_data
    elif rating_name == "强势系数B3":
        total_rating_df = all_b3_rating_data
    else:
        total_rating_df = all_b4_rating_data

    output_df = total_rating_df.loc[total_rating_df['date']>start_time]
    output_df = output_df.loc[output_df['date']<end_time]
    output_df = pd.merge(output_df, stock_basic, on='ts_code', how='left')[['name','date','rating']]
    output_df = output_df.loc[output_df['name'].isin(stock_names)]
    output_df['date'] = output_df['date'].apply(int_to_timestamp)
    output_df.columns = ["股票名称","日期",rating_name]
    return output_df

def display_data(df,expander_name,top_x,rating_name,extra_stocks_to_display):
    with st.expander(expander_name):
        st.text('以下的对比表格用强势系数的列表来排序，显示了强势系数最高的'+str(top_x)+'个股票')
        if rating_name=="强势系数B3" or rating_name=="强势系数B4":
            st.text('注：目前版本中，强势系数B3和B4只有20230101以后的数据')
        top_x_stocks = df.head(top_x)
        extra_stocks_df = df.loc[df['股票名称'].isin(extra_stocks_to_display)]
        df_to_display = pd.concat([top_x_stocks,extra_stocks_df])
        display_table(df_to_display)
        

        st.text("以下的图里每条线代表一个股票，上方对比表格里的股票都在下方的图标里面。X轴是日期，Y轴是强势系数。")
        st.text("鼠标悬浮在图里的某个点的时候可以看到那个位置的具体时间,强势系数，和股票。")
        st.text("右侧显示着每支股票对应的颜色。点击右侧的股票名称可以在图中隐藏或显示那支股票。")
        stocks_to_plot = df_to_display['股票名称']
        df_to_plot = get_df_for_plotting(stocks_to_plot,start_time,end_time,rating_name)
        px_plot = px.line(df_to_plot, x='日期', y=rating_name, color='股票名称', hover_name='股票名称')
        st.plotly_chart(px_plot)

def get_stocks_with_incomplete_data(rating_data,start_time):
    grouped_df = rating_data.groupby("ts_code").min().reset_index()
    incomplete_stocks = grouped_df.loc[grouped_df['date']>start_time]['ts_code']
    return incomplete_stocks

def get_average_rating_of_all_stocks_in_time_period(rating_name,start_time,end_time,filter_incomplete_stocks):
    if rating_name == "强势系数B1":
        raw_rating_data = all_b1_rating_data
    elif rating_name == "强势系数B2":
        raw_rating_data = all_b2_rating_data
    elif rating_name == "强势系数B3":
        raw_rating_data = all_b3_rating_data
    else:
        raw_rating_data = all_b4_rating_data
    
    output_df = raw_rating_data.loc[raw_rating_data['date']>start_time]
    output_df = output_df.loc[output_df['date']<end_time]

    if filter_incomplete_stocks:
        incomplete_stocks = get_stocks_with_incomplete_data(raw_rating_data,start_time)
        output_df = output_df.loc[~output_df['ts_code'].isin(incomplete_stocks)]

    output_df = output_df.groupby('ts_code').mean()['rating'].reset_index()
    output_df = pd.merge(output_df, stock_basic, on='ts_code', how='left')[['name','market','industry','list_date','rating']]
    output_df['list_date'] = pd.to_datetime(output_df['list_date'], format='%Y%m%d').dt.date
    output_df.columns = ["股票名称","大盘","行业","上市日期",rating_name]
    output_df = output_df.sort_values(rating_name,ascending=False)
    
    return output_df

def get_stock_name_given_code(code):
    selected_df = stock_basic.loc[stock_basic['ts_code']==code].reset_index()
    if selected_df.shape[0] == 0:
        return None
    else:
        return selected_df['name'][0]

def clean_stocks_to_display_input(raw_input):
    if raw_input == "":
        return []

    #Split by both english and chinese periods
    splitted_list_stage_1 = raw_input.split(",")
    splitted_list = []
    for i in splitted_list_stage_1:
        result_list = i.split("，")
        splitted_list.extend(result_list)

    processed_results = []
    for stock_name_or_id in splitted_list:
        if "." in stock_name_or_id:
            stock_name = get_stock_name_given_code(stock_name_or_id)
            if stock_name is None:
                st.error(f"没有找到‘{stock_name_or_id}’对应的股票数据，请确认代码输入正确")
            processed_results.append(stock_name)
        else:
            processed_results.append(stock_name_or_id)

    return processed_results

#-------------------------------------------------

st.title("股票强势系数分析-V3")
st.header("输入参数")

start_time = int(st.text_input("以下输入开始计算强势系数的时间。格式是YYYYMMDD",value="20220915"))
end_time = int(st.text_input("以下输入停止计算强势系数的时间",value="20230323"))
top_rows_displayed = int(st.text_input("计算出结果后因该显示多少个强势系数最高的股票",value=10))
specific_stocks_to_display_raw = st.text_input("下面可以添加你特比想关注的股票（空白代表不需要添加。可接受股票代码或者名称。比如说“平安银行”或“000001.SZ”。可以同时选择多个股票，注意用逗号分离。）",value="")
specific_stocks_to_display = clean_stocks_to_display_input(specific_stocks_to_display_raw)
filter_incomplete_stocks = not st.checkbox("有些股票会在开始日期之后上市，是否显示后来上市的股票？这些股票会缺失数据，可能会具有更高的强势系数。",False)
#b1_ma_days = int(st.text_input("B1使用的均线天数（可参考B1公式）",value=5))
#b2_ma_days = int(st.text_input("B2使用的均线天数（可参考B2公式）",value=5))
#b3_time_segment = int(st.text_input("B3涨速时段时长（可参考B3定义文档）",value=5))
#b4_time_segment = int(st.text_input("B4涨速时段时长（可参考B4定义文档）",value=5))
#b3_top_segment_count = int(st.text_input("B3相对涨速最靠前的数量（可参考B3定义文档）",value=3))
#b4_top_segment_count = int(st.text_input("B4相对涨速最靠前的数量（可参考B4定义文档）",value=3))
#b3_index_scale_factor = int(st.text_input("B3板块涨速放大因子（可参考B3定义文档）",value=1))
#b4_index_scale_factor = int(st.text_input("B4大盘涨速放大因子（可参考B4定义文档）",value=1))

print(f"start time is: {start_time}")

with st.spinner("正在计算强势系数。。。"):
    b1_ratings = get_average_rating_of_all_stocks_in_time_period("强势系数B1",start_time,end_time,filter_incomplete_stocks)
    b2_ratings = get_average_rating_of_all_stocks_in_time_period("强势系数B2",start_time,end_time,filter_incomplete_stocks)
    b2_market_1,b2_market_2,b2_market_3,b2_market_4 = split_by_market(b2_ratings)
    b3_ratings = get_average_rating_of_all_stocks_in_time_period("强势系数B3",start_time,end_time,filter_incomplete_stocks)
    b4_ratings = get_average_rating_of_all_stocks_in_time_period("强势系数B4",start_time,end_time,filter_incomplete_stocks)
    b4_market_1,b4_market_2,b4_market_3,b4_market_4 = split_by_market(b4_ratings)


st.header("计算结果")
display_data(b1_ratings,"根据强势系数B1排序的股票",top_rows_displayed,"强势系数B1",specific_stocks_to_display)
display_data(b2_ratings,"根据强势系数B2排序的股票",top_rows_displayed,"强势系数B2",specific_stocks_to_display)
display_data(b2_market_1,"根据强势系数B2排序的主板股票",top_rows_displayed,"强势系数B2",specific_stocks_to_display)
display_data(b2_market_2,"根据强势系数B2排序的科创板股票",top_rows_displayed,"强势系数B2",specific_stocks_to_display)
display_data(b2_market_3,"根据强势系数B2排序的创业板股票",top_rows_displayed,"强势系数B2",specific_stocks_to_display)
display_data(b2_market_4,"根据强势系数B2排序的北交所股票",top_rows_displayed,"强势系数B2",specific_stocks_to_display)
display_data(b3_ratings,"根据强势系数B3排序的股票",top_rows_displayed,"强势系数B3",specific_stocks_to_display)
display_data(b4_ratings,"根据强势系数B4排序的股票",top_rows_displayed,"强势系数B4",specific_stocks_to_display)
display_data(b4_market_1,"根据强势系数B4排序的主板股票",top_rows_displayed,"强势系数B4",specific_stocks_to_display)
display_data(b4_market_2,"根据强势系数B4排序的科创板股票",top_rows_displayed,"强势系数B4",specific_stocks_to_display)
display_data(b4_market_3,"根据强势系数B4排序的创业板股票",top_rows_displayed,"强势系数B4",specific_stocks_to_display)