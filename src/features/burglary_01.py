#!/usr/bin/env python
# coding: utf-8

import gmaps
import warnings
warnings.filterwarnings('ignore')
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns

sns.set(rc={'figure.figsize':(12, 6),"font.size":20,"axes.titlesize":20,"axes.labelsize":20},style="darkgrid")


# Is there any connection with the crime and food inspection failures? May be !\
# For now, I am focusing on the burgalaries only. The burglary data is the chicago's crime 
# data filtered for burgalaries only (in the same time window i.e. first 3 months of 2019).

burglary = pd.read_json('../data/raw/burglary.json', convert_dates=['date'])
burglary.head()

shape = burglary.shape
print(" There are %d rows and %d columns in the data" % (shape[0], shape[1]))
print(burglary.info())

# Let's check if there are any null values in the data. 
print(burglary.isna().sum())

burglary['latitude'].fillna(burglary['latitude'].mode()[0], inplace=True)
burglary['longitude'].fillna(burglary['longitude'].mode()[0], inplace=True)

ax = sns.countplot(x="ward", data=burglary)
plt.title("Burglaries by Ward")
plt.show()

plt.rcParams['figure.figsize'] = 16, 5
ax = sns.countplot(x="community_area", data=burglary)
plt.title("Burglaries by Ward")
plt.show()

# Burglaries HeatMap
APIKEY= os.getenv('GMAPAPIKEY')
gmaps.configure(api_key=APIKEY)

def make_heatmap(locations, weights=None):
    fig = gmaps.figure()
    heatmap_layer = gmaps.heatmap_layer(locations)
    #heatmap_layer.max_intensity = 100
    heatmap_layer.point_radius = 8
    fig.add_layer(heatmap_layer)
    return fig
    

locations = zip(burglary['latitude'], burglary['longitude'])
fig = make_heatmap(locations)

burglary_per_day = pd.DataFrame()
burglary_per_day = burglary[['date', 'case_number']]
burglary_per_day = burglary_per_day.set_index(
    pd.to_datetime(burglary_per_day['date']))
burglary_per_day = burglary_per_day.resample('D').count()
plt.rcParams['figure.figsize'] = 12, 5
fig, ax = plt.subplots()
fig.autofmt_xdate()
#
#ax.xaxis.set_major_locator(mdates.MonthLocator())
#ax.xaxis.set_minor_locator(mdates.DayLocator())
monthFmt = mdates.DateFormatter('%Y-%b')
ax.xaxis.set_major_formatter(monthFmt)

plt.plot(burglary_per_day.index, burglary_per_day, 'r-')
plt.xlabel('Date')
plt.ylabel('Number of Cases Reported')
plt.title('Burglaries Reported')
plt.show()

burglary['event_date'] = burglary['date']
burglary = burglary.set_index('event_date')
burglary.sort_values(by='date', inplace=True)
burglary.head()

burglary.to_csv('../data/processed/burglary_data_processed.csv')