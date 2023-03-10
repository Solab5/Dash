# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_dash.ipynb.

# %% auto 0
__all__ = ['df_agg', 'df_agg_sub', 'df_comments', 'df_time', 'df_agg_diff', 'metric_date_12mo', 'median_agg', 'numeric_cols',
           'df_time_diff', 'date_12mo', 'df_time_diff_yr', 'views_days', 'views_cumulative', 'add_sidebar',
           'style_negative', 'style_positive', 'audience_simple', 'load_data']

# %% ../nbs/00_dash.ipynb 3
def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try: 
        return props if v < 0 else None
    except:
        pass
    

# %% ../nbs/00_dash.ipynb 4
def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try: 
        return props if v > 0 else None
    except:
        pass    
    

# %% ../nbs/00_dash.ipynb 5
def audience_simple(country):
    """Show top represented countries"""
    if country == 'US':
        return 'USA'
    elif country == 'IN':
        return 'India'
    else:
        return 'Other'

# %% ../nbs/00_dash.ipynb 8
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
from datetime import datetime 

# %% ../nbs/00_dash.ipynb 11
def load_data():
    df_agg = pd.read_csv("/home/morris/gradio/Dash/files/Aggregated_Metrics_By_Video.csv").iloc[1:,:] 
    df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                          'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                          'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']

    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'])
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending = False, inplace = True)

    df_agg_sub = pd.read_csv("/home/morris/gradio/Dash/files/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv")
    df_comments = pd.read_csv("/home/morris/gradio/Dash/files/All_Comments_Final.csv")
    df_time = pd.read_csv("/home/morris/gradio/Dash/files/Video_Performance_Over_Time.csv")
    df_time['Date'] = pd.to_datetime(df_time['Date'])
    
    return df_agg, df_agg_sub, df_comments, df_time

# %% ../nbs/00_dash.ipynb 13
df_agg, df_agg_sub, df_comments, df_time = load_data()

# %% ../nbs/00_dash.ipynb 15
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months =12)
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median()

# %% ../nbs/00_dash.ipynb 17
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)

# %% ../nbs/00_dash.ipynb 19
df_time_diff = pd.merge(df_time, df_agg.loc[:,['Video','Video publish time']], left_on ='External Video ID', right_on = 'Video')
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days

# %% ../nbs/00_dash.ipynb 21
date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months =12)
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

# %% ../nbs/00_dash.ipynb 23
views_days = pd.pivot_table(df_time_diff_yr,index= 'days_published',values ='Views', aggfunc = [np.mean,np.median,lambda x: np.percentile(x, 80),lambda x: np.percentile(x, 20)]).reset_index()
views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:,['days_published','median_views','80pct_views','20pct_views']] 
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()

# %% ../nbs/00_dash.ipynb 25
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics','Individual Video Analysis'))
