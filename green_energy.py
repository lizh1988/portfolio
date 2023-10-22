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


warnings.filterwarnings('ignore')

df_data=pd.read_excel('Data-file-Europe-Power-Sector-2020.xlsx', sheet_name='Data')