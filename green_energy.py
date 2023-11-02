import pandas as pd 
import numpy as np 
import seaborn as sns
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import warnings
import pygwalker as pyg
import sqlite3
#import sqlalchemy
#from sqlalchemy import create_engine
from sqlalchemy.dialects import sqlite
from pandas.io import sql
import subprocess
import re
import openpyxl
import streamlit as st
import json


warnings.filterwarnings('ignore')

st.set_page_config(page_title="Energy production in Europe (including the UK)", layout='wide', initial_sidebar_state='expanded')
st.header("Renewable vs non-renewable energy in Europe (including the UK)🍃", divider='blue')

filename='Data-file-Europe-Power-Sector-2020.xlsx'
jsonfile='countries.geojson'
@st.cache_data
def read(filename):
    df=pd.read_excel('Data-file-Europe-Power-Sector-2020.xlsx', sheet_name='Data')
    return(df)
@st.cache_data
def load(jsonfile):
    borders=json.load(open(jsonfile,'r'))
    return(borders)

df=read(filename)
borders=load(jsonfile)


renew= ['Nuclear','Hydro','Wind','Solar','Bioenergy','Other renewables']
fossil=['Hard Coal','Lignite','Gas','Other fossil']

st.markdown(" <style> div[class^='block-container'] { padding-top: 1.7rem; } </style> ", unsafe_allow_html=True)

selected_date=st.sidebar.select_slider('Please select the year that you are interested in:',options=df.Year.unique())
selected_area=st.sidebar.selectbox('Please select the area that you are interested in:',options=df.Area.unique())
dftemp=df.loc[df['Year']==selected_date]
filter_df=dftemp.loc[df['Area']==selected_area]

#st.write(filter_df)

def renew_metric():
    fig=go.Figure()
    
    total_needs=dftemp.loc[dftemp['Area']=='EU27+1',['Generation (TWh)','Variable', 'Change on last year (TWh)']]
    top_range=total_needs.loc[total_needs['Variable']=='Demand','Generation (TWh)']
    
    
    fig.add_trace(go.Indicator(
    mode='number+gauge+delta',
    value = total_needs.loc[(total_needs['Variable']=='Renewables') | (total_needs['Variable']=='Nuclear'), 'Generation (TWh)'].sum(),
    number={'suffix':" TWh"},
    delta = {'reference': (total_needs.loc[(total_needs['Variable']=='Renewables') | (total_needs['Variable']=='Nuclear'), 'Generation (TWh)'].sum() - total_needs.loc[(total_needs['Variable']=='Renewables') | (total_needs['Variable']=='Nuclear'), 'Change on last year (TWh)'].sum())},
    gauge = {
        'axis': {'range':[0,top_range.iloc[0]],'visible': True}
        },
    domain = {'row': 0, 'column': 0},
    title = {'text':f'Renewables in EU27+1, year {selected_date}'}))

    fig.update_layout()
    st.plotly_chart(fig, use_container_width=True)

def fossil_metric():
    fig=go.Figure()
    
    total_needs=dftemp.loc[dftemp['Area']=='EU27+1',['Generation (TWh)','Variable', 'Change on last year (TWh)']]
    top_range=total_needs.loc[total_needs['Variable']=='Demand','Generation (TWh)']
    
    
    fig.add_trace(go.Indicator(
    mode='number+gauge+delta',
    value = total_needs.loc[(total_needs['Variable']=='Fossil'), 'Generation (TWh)'].sum(),
    number={'suffix':" TWh"},
    delta = {'reference': (total_needs.loc[(total_needs['Variable']=='Fossil'), 'Generation (TWh)'].sum() - total_needs.loc[(total_needs['Variable']=='Fossil'), 'Change on last year (TWh)'].sum()), 'increasing':{'color':'red'}, 'decreasing':{'color':'green'}},
    gauge = {'axis': {'range':[0,top_range.iloc[0]],'visible': True}, 'bar' : {'color':'red'}},
    domain = {'row': 0, 'column': 0},
    title = {'text':f'Fossil fuels in EU27+1, year {selected_date}'}
    ))

    fig.update_layout()
    st.plotly_chart(fig, use_container_width=True)

def bar_chart():
    dftemp=df.loc[df['Area']==selected_area]

    totalrenew=dftemp.loc[dftemp['Variable']== 'Nuclear','Generation (TWh)'], dftemp.loc[dftemp['Variable']== 'Renewables', 'Generation (TWh)']
    years=dftemp.Year.unique()
    #st.write(years)
    dftemp1=pd.DataFrame()

    
    for i in years:
        dftemp1['Year']=[i]
        dftemp1['Area']=selected_area
        dftemp1['Variable']=['renew']
        dftemp1['Generation (TWh)'] = (dftemp.loc[(dftemp['Variable']== 'Nuclear') & (dftemp['Year']==i),'Generation (TWh)'].values + dftemp.loc[(dftemp['Variable']== 'Renewables') & (dftemp['Year']==i) , 'Generation (TWh)'].values)
        
        dftemp=pd.concat([dftemp,dftemp1])
        
    #st.write(dftemp)
    # fig=go.Figure()
    # fig.add_trace(
    #     go.Histogram(x=years, y=[dftemp.loc[dftemp['Variable']== 'Fossil', 'Generation (TWh)'], dftemp.loc[dftemp['Variable']== 'renew', 'Generation (TWh)']])
    # )
    # fig.update_layout(barmode='relative')
    # fig.update_layout()
    # st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(
                dftemp, x=range(2000,2021),
                y=[(dftemp.loc[dftemp['Variable']== 'Fossil', 'Generation (TWh)']),(dftemp.loc[dftemp['Variable']== 'renew', 'Generation (TWh)'])], 
                #color="medal",
                barnorm='percent', text_auto='.2f',
                title=(f"Energy generation in {selected_area}"),
                nbins=21,
                color_discrete_map = {'wide_variable_0':'red','wide_variable_1':'green'})
    newnames = {'wide_variable_1':'Renewable energy<br>(including nuclear)', 'wide_variable_0': 'Fossil fuels'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    fig.update_layout(
    xaxis_title="Year", yaxis_title="Percentage of energy generated", legend_title_text='Energy generated'
    )
    st.plotly_chart(fig,use_container_width=True)

def sunburst():
    

    filter_df.loc[filter_df['Variable'].isin(renew), 'Category'] = 'Renewables'
    filter_df.loc[filter_df['Variable'].isin(fossil), 'Category'] = 'Fossil fuels'
    temp_df=filter_df.dropna(subset=['Category'], inplace=False)
    #st.write(temp_df)

    fig=px.sunburst(
        temp_df, path=['Category','Variable'], values='Generation (TWh)', title=f'Energy generation of {selected_area}', color_discrete_sequence=['green','red']
        )
    # color_map={
    #         'Renewables':'#008000',
    #         'Fossil fuels':'#ff0000',
    #         'Hard Coal':'#f44336',
    #         'Lignite':'#ea9999',
    #         'Gas':'#cc0000',
    #         'Other fossil':'#990000',
    #         'Nuclear':'#adf703',
    #         'Hydro':'#03f708',
    #         'Wind':'#9edf9f',
    #         'Solar':'#308932',
    #         'Bioenergy':'#14ec77',
    #         'Other renewables':'#83dfad'
    #     }
    #fig.update_traces(marker_colors=[color_map[cat] for cat in fig.data[-1].labels])
    fig.update_layout(margin=dict(l=20, r=20, t=25, b=20))
    st.plotly_chart(fig, use_container_width=True)

def heatmap():
    dftemp.loc[dftemp['Variable'].isin(renew), 'Category'] = 'Renewables'
    dftemp.loc[dftemp['Variable'].isin(fossil), 'Category'] = 'Fossil fuels'
    temp_df=dftemp.dropna(subset=['Category'], inplace=False)
    
    temp_df=temp_df[temp_df['Category']=='Renewables']
    temp_df=temp_df[temp_df['Area']!='EU-27']
    temp_df=temp_df[temp_df['Area']!='EU27+1']
    map_df=pd.DataFrame()
    map_df1=pd.DataFrame()



    for i in pd.unique(temp_df['Area']):
        #st.write(i)
        map_df1['Area']=[i]
        #map_df1['greeness']=temp_df.query("Area==@i")['Share of production (%)'].sum()
        tempnum=sum(temp_df.loc[temp_df['Area']==i,'Share of production (%)'].values)
        map_df1['Renewables']=tempnum
        #st.write(map_df1)
        map_df=pd.concat([map_df,map_df1])
        
        #dftemp1['Generation (TWh)'] = (dftemp.loc[(dftemp['Variable']== 'Nuclear') & (dftemp['Year']==i),'Generation (TWh)'].values + dftemp.loc[(dftemp['Variable']== 'Renewables') & (dftemp['Year']==i) , 'Generation (TWh)'].values)

    #st.write(pd.unique(temp_df['Area']))
    #st.write(map_df)
    fig = px.choropleth(map_df,geojson=borders, locations='Area', scope='europe', locationmode='country names', color=map_df['Renewables'], title=f'Percentage of energy generated by renewable sources in {selected_date}', 
    color_continuous_scale="Greens"
    )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(margin=dict(t=23, b=0, l=0, r=0))
    st.plotly_chart(fig,use_container_width=True)




col1,col2,col3 = st.columns([1,1,2])

with col1:
    renew_metric()

with col2:
    fossil_metric()

with col3:
    bar_chart()

col4,col5 = st.columns([1,2])

with col4:
    sunburst()

with col5:
    heatmap()