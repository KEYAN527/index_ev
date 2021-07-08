# -*- coding: utf-8 -*-
"""
Created on Wed Jul  7 13:51:29 2021

@author: Administrator
"""

from pyecharts import options as opts
from pyecharts.charts import Bar, Grid, Line,Scatter
from pyecharts.commons.utils import JsCode

from scipy import stats 

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
    
    index_value_all = pd.read_excel(index_value_path)
    index_name = indexFund_all[['标的指数','name']].drop_duplicates().rename(columns = {'标的指数':'index'},inplace = False)
    index_value_all = index_value_all.merge(index_name,on =['index'],how = 'left')
    del index_name
    
    name_list = list(set(indexFund_all['name']))
    
    ###行业指数列表    
    st.title('指数景气度总览')
    index_value_all = index_value_all.rename(columns = {'Unnamed: 0':'日期'},inplace = False)
    index_value_all = index_value_all.sort_values(['name','日期'])
    index_qtl = index_value_all.groupby(['name']).apply(lambda x:np.round(stats.percentileofscore(x['PE_TTM'], x['PE_TTM'].values[-1]),2)).reset_index()
    index_qtl.columns = ['指数名称','估值分位（%）']
    index_yoy = index_value_all[index_value_all['YOY_OR'].notnull()].groupby(
            ['name']).apply(lambda x:np.round(x['YOY_OR'].values[-1],3)).reset_index()
    index_yoy.columns = ['指数名称','营业收入同比增长（%）']    
    index_qtl = pd.merge(index_qtl,index_yoy,on = ['指数名称'],how = 'left')
    
    index_qtl = index_qtl[(index_qtl['估值分位（%）'].notnull())&
                          (index_qtl['营业收入同比增长（%）'].notnull())].sort_values(['营业收入同比增长（%）'])
    scatter_data = []
    for i in range(len(index_qtl)):
        set_i = {'value':100-index_qtl['估值分位（%）'].values[i],'text':index_qtl['指数名称'].values[i]}
        scatter_data = scatter_data+[set_i]
        
    index_scatter = Scatter(init_opts=opts.InitOpts(width="1100px", height="500px")).add_xaxis(
            xaxis_data=list(round(index_qtl['营业收入同比增长（%）'],2))
            ).add_yaxis(series_name="100-估值分位（%）",y_axis=scatter_data,
                       symbol_size=15,
                       label_opts=opts.LabelOpts(formatter = JsCode('''function(params){return params.data.text;}''')
                       ,is_show=False),
        ).set_global_opts(
                yaxis_opts=opts.AxisOpts(
                        type_="value",
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True),
                        ),tooltip_opts=opts.TooltipOpts(formatter = JsCode('''function(params){return params.data.text;}'''),is_show=True
                        ),visualmap_opts=opts.VisualMapOpts(max_=100),
                        ).render("scatter.html")
    components.html(open(index_scatter, 'r', encoding='utf-8').read(),width = 1100,height = 500)
    st.text('*横轴为当前营业收入同比增长率（%）；纵轴为当前100减去估值水平；')
    
    
    ###单个指数详情
    st.title('指数景气度详情')    
    # Render file dropbox
    with st.beta_container(): 
        name_select = st.selectbox('', tuple(name_list))
    
    index_value = index_value_all.loc[index_value_all['name'] == name_select,:]
    del index_value_all
    
    st.header('跟踪该指数的基金产品')
    index_fund = indexFund_all.loc[indexFund_all['name']==name_select,['标的指数','指数名称','基金代码','基金名称','规模合计','管理费率','托管费率']]
    index_fund['规模合计'] = index_fund['规模合计']/100000000
    index_fund = index_fund.rename(columns = {'规模合计':'规模合计（亿元元）','管理费率':'管理费率（%）','托管费率':'管理费率（%）'},inplace = False)
    st.table(index_fund)
    
    
    st.header('行业估值/盈利信息')
    
    qtl_now = np.round(stats.percentileofscore(index_value['PE_TTM'], index_value['PE_TTM'].values[-1]),2)
    st.info('当前估值水平处于近3年'+str(qtl_now)+'%分位数的水平')
    
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
    
    index_bar = index_value[(index_value['YOY_OR'].notnull())|(index_value['YOYNETPROFIT'].notnull())]
    index_plt_bar =  Bar(init_opts = opts.InitOpts(width = '1100px',height = '500px')).add_xaxis(
            [str(i)[:10] for i in list(index_bar['日期'])]
            ).add_yaxis('营业收入增长率（同比）:%',list(index_bar['YOY_OR']),color = "#708090"
            ).add_yaxis('归母同比净利润增长率（同比）:%',list(index_bar['YOYNETPROFIT']),color = "#B22222"
                    ).set_series_opts(label_opts=opts.LabelOpts(is_show=False),
                    ).set_global_opts(yaxis_opts=opts.AxisOpts(name = '同比增长率:%',position= 'left',
                        axisline_opts=opts.AxisLineOpts(
                                   linestyle_opts=opts.LineStyleOpts(color="#B22222")),
                        min_= min(index_bar['YOY_OR'].min(),index_bar['YOYNETPROFIT'].min())),datazoom_opts=opts.DataZoomOpts()
                    ).render('indexbar.html')  

    components.html(open(index_plt_bar, 'r', encoding='utf-8').read(),width = 1100,height = 500)


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
        
