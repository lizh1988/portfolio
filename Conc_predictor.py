import cloudpickle as cp
import sklearn as sk
from sklearn import *
import streamlit as st
import pandas as pd
import numpy as np
import sklearn as sk
import xgboost as xgb
import tensorflow as tf
import keras as ks
import seaborn as sns
import plotly.express as px
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials, space_eval
import warnings
from urllib.request import urlopen
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Concrete strength predictor", layout='wide')
st.title("Predict your concrete strength here!")
st.write('Enter the values of your mix design in kg/m³, age in days')
'---'
#Reading CSV file
filename = 'https://github.com/lizh1988/portfolio/raw/main/regoptparams.pkl'

regopt = cp.load(urlopen(filename))


factor=['Fly ash', 'Blast furnace slag', 'Superplasticizer', 'Water', 'Cement', 'Coarse aggregate', 'Fine aggregate']

st.session_state.df = pd.DataFrame(columns=['cement', 'slag', 'water', 'ash', 'sp', 'coarse',
                          'fine', 'age'])

st.header('Input your mix design here:', divider='rainbow')
with st.form('inputform', clear_on_submit=False):
    with st.expander('Input'):
        for i in factor:
            st.number_input(f'{i}:', min_value=0, format='%i', key=i)
        st.slider('Age in days', min_value=7, max_value=28, step=7, key='age')
    calculate=st.form_submit_button('Calculate concrete strength!')
    if calculate:
        df = pd.DataFrame()
        st.session_state.df['cement'] = int(st.session_state['Cement'])
        st.session_state.df['slag'] = int(st.session_state['Blast furnace slag'])
        st.session_state.df['water'] = int(st.session_state['Water'])
        st.session_state.df['ash'] = int(st.session_state['Fly ash'])
        st.session_state.df['sp'] = int(st.session_state['Superplasticizer'])
        st.session_state.df['coarse'] = int(st.session_state['Coarse aggregate'])
        st.session_state.df['fine'] = int(st.session_state['Fine aggregate'])
        st.session_state.df['age'] = int(st.session_state['age'])
        
        st.session_state.df = pd.concat([df, pd.DataFrame({'cement': [int(st.session_state['Cement'])], 
                              'slag': [int(st.session_state['Blast furnace slag'])], 
                              'ash': [int(st.session_state['Fly ash'])],
                              'water': [int(st.session_state['Water'])], 
                              'sp': [int(st.session_state['Superplasticizer'])], 
                              'coarse': [int(st.session_state['Coarse aggregate'])],
                              'fine': [int(st.session_state['Fine aggregate'])], 
                              'age': [int(st.session_state['age'])] 
                              })], axis=0)
        
        y_pred=regopt.predict(st.session_state.df)
        st.info(f'The predicted concrete strength is {y_pred} MPa.')       