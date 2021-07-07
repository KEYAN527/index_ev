# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:51:29 2021

@author: Administrator
"""

from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line

from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

def main(index_info_path,index_value_path):
    '''Add control flows to organize the UI sections. '''
#    st.sidebar.image('./docs/logo.png', width=250)
    indexFund_all = pd.read_excel(index_info_path)
    indexFund_all = indexFund_all[(indexFund_all['发行分类']=='主题')|(indexFund_all['发行分类']=='行业')]
    indexFund_all['name'] = indexFund_all['指数名称']+'('+indexFund_all['发行系列']+')'
    
    index_value = pd.read_excel(index_value_path)
    name_list = list(set(indexFund_all['name']))

    st.title('行业/主题指数景气度分析')    
    # Render file dropbox
    with st.beta_container(): 
        name_select = st.selectbox('', tuple(name_list))
    
    index_select = indexFund_all.loc[indexFund_all['name']==name_select,'标的指数'].values[0]
    index_value = index_value.loc[index_value['index'] == index_select,:]
    index_value = index_value.rename(columns = {'Unnamed: 0':'日期'},inplace = False)
    
    index_fund = indexFund_all.loc[indexFund_all['标的指数']==index_select,['标的指数','指数名称','基金代码','基金名称','规模合计','管理费率','托管费率']]
    st.table(index_fund)
    
    index_plt1 = Line(init_opts = opts.InitOpts(width = '1100px',height = '500px')).add_xaxis(
            [str(i)[:10] for i in list(index_value['日期'])]
            ).add_yaxis('指数净值',list(index_value['CLOSE']),yaxis_index = 0,color = "#708090"
            ).add_yaxis('指数PE_TTM',list(index_value['PE_TTM']),yaxis_index = 1,color="#4682B4"
            ).add_yaxis('PE_TTM_50%',[np.round(index_value['PE_TTM'].median(),2)]*len(index_value),yaxis_index = 1,color="#B22222",
                       label_opts=opts.LabelOpts(is_show=False),
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.1, color="#708090")
            ).extend_axis(
                    yaxis=opts.AxisOpts(
                            name="指数PE_TTM",
                            type_="value",
                            position="right",
                            axisline_opts=opts.AxisLineOpts(
                                   linestyle_opts=opts.LineStyleOpts(color="#4682B4")),
  #                          axislabel_opts=opts.LabelOpts(formatter="{value} ml"),
                            )

                    ).set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                    ).set_global_opts(yaxis_opts=opts.AxisOpts(name = '指数净值',position= 'left',
                        axisline_opts=opts.AxisLineOpts(
                                   linestyle_opts=opts.LineStyleOpts(color="#B22222")),
                        min_=np.round(index_value['CLOSE'].min(),0)-100),datazoom_opts=opts.DataZoomOpts()
                    ).render('indexline.html')  
            
    components.html(open(index_plt1, 'r', encoding='utf-8').read(),width = 1100,height = 500)

    index_plt2 = Line(init_opts = opts.InitOpts(width = '1100px',height = '500px')).add_xaxis(
            [str(i)[:10] for i in list(index_value['日期'])]
            ).add_yaxis('指数净值',list(index_value['CLOSE']),color ="#F08080"
            ).add_yaxis(str(np.round(index_value['PE_TTM'].mean()+10,2))+'X_PE',np.round(index_value['PE_TTM'].mean()+10,2)*(index_value['CLOSE']/index_value['PE_TTM']),color="#FFA500",
                       label_opts=opts.LabelOpts(is_show=False),
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.1, color="#708090")
            ).add_yaxis(str(np.round(index_value['PE_TTM'].mean()+5,2))+'X_PE',np.round(index_value['PE_TTM'].mean()+5,2)*(index_value['CLOSE']/index_value['PE_TTM']),color="#FFD700",
                       label_opts=opts.LabelOpts(is_show=False),
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.1, color="#808080")
            ).add_yaxis(str(np.round(index_value['PE_TTM'].mean(),2))+'X_PE',np.round(index_value['PE_TTM'].mean(),2)*(index_value['CLOSE']/index_value['PE_TTM']),color="#808080",
                       label_opts=opts.LabelOpts(is_show=False),
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.3, color="#FFD700")
            ).add_yaxis(str(np.round(index_value['PE_TTM'].mean()-5,2))+'X_PE',np.round(index_value['PE_TTM'].mean()-5,2)*(index_value['CLOSE']/index_value['PE_TTM']),color= "#708090",
                       label_opts=opts.LabelOpts(is_show=False),
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.4, color="#FFA500")
            ).add_yaxis(str(np.round(index_value['PE_TTM'].mean()-10,2))+'X_PE',np.round(index_value['PE_TTM'].mean()-10,2)*(index_value['CLOSE']/index_value['PE_TTM']),color="#B22222",
                       label_opts=opts.LabelOpts(is_show=False),
                       areastyle_opts=opts.AreaStyleOpts(opacity=0.8, color="#F08080")
                    
                    ).set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                    ).set_global_opts(yaxis_opts=opts.AxisOpts(name = '指数净值',position= 'left',
                        axisline_opts=opts.AxisLineOpts(
                                   linestyle_opts=opts.LineStyleOpts(color="#B22222")),
                        min_=np.round(index_value['CLOSE'].min(),0)-100),datazoom_opts=opts.DataZoomOpts()
                    ).render('indexline.html')  
            
    components.html(open(index_plt2, 'r', encoding='utf-8').read(),width = 1100,height = 500)


if __name__ == '__main__': 
    st.set_page_config(page_title='行业/主题景气程度测试系统', layout='wide', initial_sidebar_state='auto')
    try: 
        main(index_info_path = './data/权益类ETF产品列表.xlsx',
             index_value_path = './data/指数估值信息汇总.xlsx')
    except: 
        st.error('Oops! Something went wrong...Please check your input.\nIf you think there is a bug. ')
        raise
        
