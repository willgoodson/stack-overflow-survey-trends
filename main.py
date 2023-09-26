import pandas as pd
import plotly.express as px
import numpy as np
## DEFINE NEEDED ARRAYS
use_cols = ['MainBranch', 'DevType', 'ConvertedCompYearly', 'EdLevel', 'LanguageHaveWorkedWith']
drop_cols = ['is_dev']
figs = []
## IMPORT DATA FROM CSV ##
datax = pd.read_csv('./survey_results_public.csv', usecols=use_cols)
datax = datax.rename(columns={'MainBranch': 'is_dev', 'DevType': 'role', 'ConvertedCompYearly': 'salary', 'EdLevel': 'education', 'LanguageHaveWorkedWith': 'languages'})
## DELETE ANY ROWS CONTAINING NULL DATA ##
filtered_data = datax.dropna()
## FILTER: USE ONLY DATA FROM "PROFESSIONAL" DEVELOPERS
filtered_data = filtered_data[(filtered_data['is_dev'] == 'I am a developer by profession')]
filtered_data['languages'] = filtered_data['languages'].str.split(';')
filtered_data = filtered_data.drop(drop_cols, axis=1)
## GET EDUCATION LEVELS FROM DATA ##
education_levels = filtered_data['education'].unique()
## CREATE BOX PLOTS ##
for education_level in education_levels:
    ## FILTER: EDUCATION LEVEL
    data_subset = filtered_data[filtered_data['education'] == education_level]
    ## FLATTEN LANGUAGES LIST TO CREATE SEPARATE ENTRIES ##
    data_subset = data_subset.explode('languages')
    # FILTER: REMOVE EXTREMELY LOW SALARIES (BAD DATA?). I JUST FILTERED IS BY THE POVERTY WAGE FOR AN INDIVIDUAL ##
    data_subset = data_subset[(data_subset['salary'] >= 15000)]
    ## CALCULATE INTERQUARTILE RANGE FOR SALARY ##
    Q1 = data_subset['salary'].quantile(0.25)
    Q3 = data_subset['salary'].quantile(0.75)
    IQR = Q3 - Q1
    ## DEFINE UPPER AND LOWER BOUNDS OF PLOT ##
    lower_bound = Q1 - 1.75 * IQR
    upper_bound = Q3 + 1.75 * IQR
    ## FILTER: REMOVE EXTREME OUTLIERS
    data_subset = data_subset[(data_subset['salary'] >= lower_bound) & (data_subset['salary'] <= upper_bound)]
    ## FILTER: ONLY INCLUDE TOP N LANGUAGES
    data_subset = data_subset[data_subset['languages'].isin(data_subset['languages'].value_counts().nlargest(20).index)]
    ## CREATE BOX PLOT ##
    fig = px.box(data_subset, x='languages', y='salary', color='languages',
                 title=f'Salary Distribution by Programming Language for {education_level}',
                 labels={'languages': 'Programming Language', 'salary': 'Salary'})
    ## GENERATE Y AXIS VALUES ##
    y_axis_range = np.arange(0, upper_bound + 50000, 50000)
    y_axis_ticktext = [f"${int(salary/1000)}K" for salary in y_axis_range]
    y_axis_tickvals = y_axis_range
    ## UPDATE Y AXIS AND LEGEND ##
    fig.update_layout(showlegend=True)
    fig.update_yaxes(type="linear", range=[0, upper_bound + 50000],
                     tickmode='array', tickvals=y_axis_tickvals,
                     ticktext=y_axis_ticktext)
    ## APPEND FIGURE TO LIST ##
    figs.append(fig)
## SHOW ALL BOX BLOTS ##
for fig in figs:
    fig.show()