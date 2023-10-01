import pandas as pd 
import numpy as np 
import seaborn as sns
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import streamlit as st


st.title("ADCC statistics")
#Reading CSV file
filename = 'https://raw.githubusercontent.com/lizh1988/portfolio/main/ADCC%20data%20viz/adcc_historical_data.csv'


@st.cache_data
def read(filename):
    df = pd.read_csv(filename, sep = ';')
    df.drop(['match_id','winner_id', 'loser_id', 'winner_name','loser_name'], axis=1, inplace=True)
    return(df)

df=read(filename)

#Dropping useless entries
mask1=df.loc[(df['win_type']=='SUBMISSION') & df['submission'].isna()]
mask2=df.loc[(df['win_type']== 'INJURY') | (df['win_type']== 'DESQUALIFICATION')]
df.drop(index=mask1.index, inplace=True)
df.drop(index=mask2.index, inplace=True)

#Grouping submissions into families based on body part that they attack
df['target']=(np.nan)
upper_body=['Armbar', 'Kimura' ,'Omoplata', 'Americana' ,'Shoulder lock', 'Wristlock']
lower_body=['Inside heel hook','Outside heel hook','Heel hook' ,'Footlock' , 'Toe hold' , 'Leg lock' , 'Calf slicer', 'Dogbar' , 'Estima lock' , 'Z Lock', 'Kneebar']
neck=['RNC' , 'Katagatame' , 'Guillotine' , 'Triangle' , 'Choke' , "D'arce choke" , 'Short choke' , 'North south choke' , 'Headlock' , 'Anaconda' , 'Ezekiel' , 'Cross face' , 'Twister']
df.loc[df['submission'].isin(upper_body), 'target'] = 'Upper body'
df.loc[df['submission'].isin(lower_body), 'target'] = 'Lower body'
df.loc[df['submission'].isin(neck), 'target'] = 'Neck'   

df['submission'].replace(['Inside heel hook', 'Outside heel hook'], 'Heel hook', inplace=True)
mask=df[(df['submission']=='Submission') | (df['submission']=='Verbal tap')]
df.drop(mask.index,inplace=True, axis=0)

#Splitting the dataset into male and female datasets
dfm=df[df['sex']=='M']
dff=df[df['sex']=='F']


st.header("An analysis of ADCC matches from 1998 to 2022", divider ='red')

st.select = st.selectbox('Gender', ['Male', 'Female'])