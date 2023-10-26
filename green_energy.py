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


warnings.filterwarnings('ignore')

st.set_page_config(page_title="Energy production in Europe (including the UK)", layout='wide', initial_sidebar_state='expanded')
st.title("Renewable vs non-renewable energy in Europe (including the UK)🍃")

filename='Data-file-Europe-Power-Sector-2020.xlsx'

@st.cache_data
def read(filename):
    df=pd.read_excel('Data-file-Europe-Power-Sector-2020.xlsx', sheet_name='Data')
    return(df)

#df_data=read(filename)
#mask1=df_data.loc[(df_data['Variable']=='Net imports') | (df_data['Variable']=='Production') | (df_data['Variable']=='Demand')]
#df=df_data.drop(index=mask1.index, inplace=False)
df=read(filename)

st.write(df)

renew= ['Nuclear','Renewables','Hydro','Wind and solar','Wind','Solar','Bioenergy','Other renewables']
fossil=['Fossil','Coal','Hard Coal','Lignite','Gas','Other fossil']

#selected_date=st.sidebar.select_slider('Please select the year that you are interested in:',options=df_data.Year.unique())
selected_date=st.sidebar.select_slider('Please select the year that you are interested in:',options=df.Year.unique())
filter_df=df.loc[df['Year']==selected_date]

#st.write(filter_df)


def renew_metric():
    fig=go.Figure()
    
    total_needs=filter_df.loc[filter_df['Area']=='EU27+1',['Generation (TWh)','Variable', 'Change on last year (TWh)']]
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
    title = {'text':'Renewables'}))

    fig.update_layout()
    st.plotly_chart(fig, use_container_width=True)

def fossil_metric():
    fig=go.Figure()
    
    total_needs=filter_df.loc[filter_df['Area']=='EU27+1',['Generation (TWh)','Variable', 'Change on last year (TWh)']]
    top_range=total_needs.loc[total_needs['Variable']=='Demand','Generation (TWh)']
    
    
    fig.add_trace(go.Indicator(
    mode='number+gauge+delta',
    value = total_needs.loc[(total_needs['Variable']=='Fossil'), 'Generation (TWh)'].sum(),
    number={'suffix':" TWh"},
    delta = {'reference': (total_needs.loc[(total_needs['Variable']=='Fossil'), 'Generation (TWh)'].sum() - total_needs.loc[(total_needs['Variable']=='Fossil'), 'Change on last year (TWh)'].sum()), 'increasing':{'color':'red'}, 'decreasing':{'color':'green'}},
    gauge = {'axis': {'range':[0,top_range.iloc[0]],'visible': True}, 'bar' : {'color':'red'}},
    domain = {'row': 0, 'column': 0},
    title = {'text':'Fossil fuels'}
    ))

    fig.update_layout()
    st.plotly_chart(fig, use_container_width=True)

col1,col2 = st.columns(2)

with col1:
    renew_metric()

with col2:
    fossil_metric()