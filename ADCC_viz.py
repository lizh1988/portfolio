import pandas as pd 
import numpy as np
import plotly 
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="ADCC statistics", layout='wide', initial_sidebar_state='expanded')
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
df.loc[df['submission'].isin(upper_body), 'target'] = 'Arms'
df.loc[df['submission'].isin(lower_body), 'target'] = 'Legs'
df.loc[df['submission'].isin(neck), 'target'] = 'Neck'   

df['submission'].replace(['Inside heel hook', 'Outside heel hook'], 'Heel hook', inplace=True)
mask=df[(df['submission']=='Submission') | (df['submission']=='Verbal tap')]
df.drop(mask.index,inplace=True, axis=0)



st.header("An analysis of ADCC matches from 1998 to 2022", divider ='red')
#Selecting gender
st.sidebar.header('Choose your filters:')
genderfilter = st.sidebar.selectbox('Gender', ['Male', 'Female'])

#Splitting the dataset into male and female datasets
if genderfilter=='Male':
    dfcopy=df[df['sex']=='M']
    dfcopy['percentagecount']=0.01
    dfcopy=dfcopy.sort_values(by=["win_type"], axis=0)
elif genderfilter=='Female':
    dfcopy=df[df['sex']=='F']
    dfcopy['percentagecount']=0.01
    dfcopy=dfcopy.sort_values(by=["win_type"], axis=0)


weightfilter=st.sidebar.multiselect('Pick the weight classes you are interested in:',dfcopy['weight_class'].unique())

dfcopy=dfcopy[dfcopy['weight_class'].isin(weightfilter)]

#custom_dict=['60KG', '+60KG','66KG', '77KG', '88KG', '99KG', '+99KG', 'ABS']
#dfcopy=dfcopy.sort_values(by=["weight_class", "win_type", "target"], axis=0, key=lambda x: x.map(custom_dict))

df['weight_class'] = pd.Categorical(df['weight_class'], ordered=True, 
            categories=['60KG', '+60KG','66KG', '77KG', '88KG', '99KG', '+99KG', 'ABS'])

df['win_type'] = pd.Categorical(df['win_type'], ordered=True, 
            categories=['POINTS', 'DECISION', 'SUBMISSION'])

df['target'] = pd.Categorical(df['target'], ordered=True, 
            categories=['Arms', 'Legs', 'Neck'])

col1,col2=st.columns((1,1.5))



with col1:
    #Win type histogram
    
    hst=px.histogram(
    dfcopy, y='weight_class', x='percentagecount', title = 'Distribution of win types across weight categories',
    barmode='stack', barnorm='percent', color ='win_type',
    labels=dict(weight_class='Weight Class', percentagecount="occurence", win_type="Type of victory"),
    category_orders={'Type of victory': ['POINTS', 'DECISION', 'SUBMISSION']}
    )
    #if genderfilter=='Male':
        #hst.update_yaxes(categoryorder='array', categoryarray= ['66KG', '77KG', '88KG', '99KG', '+99KG', 'ABS'])
    #elif genderfilter=='Female':
        #hst.update_yaxes(categoryorder='array', categoryarray=['60KG', '+60KG'])

    
        

    hst.update_layout(xaxis_ticksuffix = '%', xaxis_title= 'Percentage within each weight class', height =300)

    st.plotly_chart(hst, use_container_width=True)


    #Points difference histogram
    dfpoints=dfcopy[dfcopy['win_type']=='POINTS'] 
    dfpoints['points_diff']=(dfpoints['winner_points']-dfpoints['loser_points'])
    


    
    hst1=px.histogram(
    dfpoints, x='points_diff', title = 'Distribution of points difference',
    labels=dict(points_diff='Difference in points'), color_discrete_sequence=['indianred']
    )
    hst1.update_traces(
    xbins=dict(size=1),
    )
    hst1.update_xaxes(tickson='boundaries')
    hst1.update_layout(xaxis=dict(tickmode = 'linear', tick0 = 0, dtick=1), height =400)

    st.plotly_chart(hst1, use_container_width=True)

dfsub=dfcopy[dfcopy['submission'].notnull()]
dfsub['subcounts']=1

dfsub=dfsub.sort_values(by=["weight_class","target"], axis=0)


with col2:
    
    sb=px.sunburst(
    dfsub, path=['weight_class','target','submission'], values='subcounts', color='target',
    labels={'subcounts': 'Number of occurences'}, title='Distribution of completed submissions'
    )

    sb.update_traces(textinfo="label+percent parent", insidetextorientation='horizontal')

    sb.update_layout(title='Breakdown of targets attacked and submission type by weight class', height =750)
    #st.write(sb)
    
    st.plotly_chart(sb, use_container_width=True)