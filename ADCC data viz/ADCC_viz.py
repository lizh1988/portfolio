import pandas as pd 
import numpy as np 
import seaborn as sns
import plotly.express as px
import plotly.subplots as sp
import plotly.graph_objects as go

url = 'https://raw.githubusercontent.com/lizh1988/portfolio/main/ADCC%20data%20viz/adcc_historical_data.csv'
df = pd.read_csv(url, sep = ';')
df.drop(['match_id','winner_id', 'loser_id', 'winner_name','loser_name'], axis=1, inplace=True)

mask1=df.loc[(df['win_type']=='SUBMISSION') & df['submission'].isna()]
mask2=df.loc[(df['win_type']== 'INJURY') | (df['win_type']== 'DESQUALIFICATION')]
print(mask1)
print(mask2)