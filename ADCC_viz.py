import pandas as pd 
import numpy as np 
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
dfm['percentagecount']=0.01
dff['percentagecount']=0.01
dff=dff.sort_values(by=["win_type"], axis=0)
dfm=dfm.sort_values(by=["win_type"], axis=0)

st.header("An analysis of ADCC matches from 1998 to 2022", divider ='red')
#Selecting gender
st.select = st.selectbox('Gender', ['Male', 'Female'])

#Win type histogram
if st.select=='Male':
    hst=px.histogram(
    dfm, y='weight_class', x='percentagecount', title = 'Distribution of win types across weight categories - Males',
     barmode='stack', barnorm='percent', color ='win_type',
    labels=dict(weight_class='Weight Class', percentagecount="occurence", win_type="Type of victory"),
    category_orders={'Type of victory': ['POINTS', 'DECISION', 'SUBMISSION']}
    )
    hst.update_yaxes(categoryorder='array', categoryarray= ['66KG', '77KG', '88KG', '99KG', '+99KG', 'ABS'])

elif st.select=='Female':
    hst=px.histogram(
    dff, y='weight_class', x='percentagecount', title = 'Distribution of win types across weight categories - Females', 
    color='win_type', barmode='stack', barnorm='percent',
    labels=dict(weight_class='Weight Class', percentagecount="occurence", win_type="Type of victory"),
    category_orders={"Type of victory": ["Points", "Decision", "Submission"]}
    )
    hst.update_yaxes(categoryorder='array', categoryarray=['60KG', '+60KG'])

hst.update_layout(xaxis_ticksuffix = '%', xaxis_title= 'Percentage within each weight class')

st.write(hst)


#Points difference histogram
dfmpoints=dfm[dfm['win_type']=='POINTS']
dffpoints=dff[dff['win_type']=='POINTS']

dfmpoints['points_diff']=(dfmpoints['winner_points']-dfmpoints['loser_points'])
dffpoints['points_diff']=(dffpoints['winner_points']-dffpoints['loser_points'])


if st.select=='Male':
    hst1=px.histogram(
    dfmpoints, x='points_diff', title = 'Distribution of points difference in matches where athletes won by points - Males',
    labels=dict(points_diff='Difference in points'), color_discrete_sequence=['indianred']
    )

elif st.select=='Female':
    hst1=px.histogram(
    dffpoints, x='points_diff', title = 'Distribution of points difference in matches where athletes won by points - Females',
    labels=dict(points_diff='Difference in points'), color_discrete_sequence=['indianred']
    )

    hst1.update_traces(
    xbins=dict(size=1),
    )
    hst1.update_xaxes(tickson='boundaries')
hst1.update_layout(xaxis=dict(tickmode = 'linear', tick0 = 0, dtick=1))

st.write(hst1)

dfmsub=dfm[dfm['submission'].notnull()]
dfmsub['subcounts']=1

dffsub=dff[dff['submission'].notnull()]
dffsub['subcounts']=1

dffsub=dffsub.sort_values(by=["weight_class","target"], axis=0)
dfmsub=dfmsub.sort_values(by=["weight_class","target"], axis=0)


if st.select=='Male':
    sb=px.sunburst(
    dfmsub, path=['weight_class','target','submission'], values='subcounts', color='target',
    labels={'subcounts': 'Number of occurences'}, title='Male atheletes'
    )

elif st.select=='Female':
    sb=px.sunburst(
    dffsub, path=['weight_class','target','submission'], values='subcounts', color='target',
    labels={'subcounts': 'Number of occurences'}, title='Female athletes'
    )

sb.update_traces(textinfo="label+percent parent")

sb.update_layout(title='Breakdown of targets attacked and submission type by weight class', height=800)
st.write(sb)