#!/usr/bin/env python
# coding: utf-8

import sys
import os
import re
import time
import json
import warnings
warnings.filterwarnings('ignore')
sys.path.append('/Users/dipakrimal/work/')
from neighborhoods import gps_to_neighborhood
from datetime import datetime, date, time, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set(rc={'figure.figsize':(12, 6),"font.size":20,"axes.titlesize":20,"axes.labelsize":20},style="darkgrid")
import matplotlib.dates as mdates
from datetime import datetime, date, time, timedelta
from sklearn.preprocessing import LabelEncoder
from geopy import distance
import geopy.distance
import requests
import time
private_token = os.getenv('PRIVATE_TOKEN')

#read json data into pandas data frame
food_data = pd.read_json('../data/raw/food-inspection.json',
                         convert_dates=['inspection_date'])
shape = food_data.shape
print(" So there are %d rows and %d columns in the data" %
      (shape[0], shape[1]))

# Pre-processing data

food_data['event_date'] = food_data['inspection_date'] 
food_data.rename(columns={'license_': 'license'}, inplace=True)
#food_data['inspection_date'] = food_data['inspection_date'].dt.date
#Check if the license number is valid 
food_data = food_data[np.isfinite(food_data['license'])]   
food_data = food_data[(food_data['license'] > 0)
                      & (food_data['inspection_date'] != 0)]
# Drop redudand/unnecessary columns
food_data = food_data.drop(['location', 'zip', 'state', 'city'], axis=1)
food_data['license'] = food_data['license'].astype('int')

#Fill missing data
food_data['latitude'].fillna(food_data['latitude'].mode()[0], inplace=True)
food_data['longitude'].fillna(food_data['longitude'].mode()[0], inplace=True)
food_data['aka_name'].fillna(food_data['dba_name'], inplace=True)

all_neighborhoods = gps_to_neighborhood.get_all_neighborhoods()
food_data['neighborhood'] = food_data.apply(
    lambda x: gps_to_neighborhood.find_neighborhood(x['longitude'], x[
        'latitude'], all_neighborhoods),
    axis=1)

plt.figure(figsize=(14, 6))
#food_data.unstack.plot(['inspection_date'].hist(bins=16, use_index=True)
food_data['event_date'].hist()
plt.title("Inspections by date")
plt.xlabel("Inspection Date")
plt.show()

def count_violations(row):
    """
    Splits different violations column on ('|') to separate different violations and counts each type of violations
    input: dataframe row
    output: list of number of different types of violations
    """
    if row['violations'] is None:
        return [0]
    else:
        serious_violations_count = 0
        critical_violations_count = 0
        minor_violations_count = 0
        x = row['violations'].split('|')
        if row['inspection_date'] < pd.to_datetime('2018-07-01'):
            codes = []
            for violation in x:
                match = int(re.search('[0-9]+', violation).group())
                #print(match)
                codes.append(match)
            for code in codes:
                if code < 15:
                    critical_violations_count += 1
                elif code > 15 and code < 30:
                    serious_violations_count += 1
                elif (code > 30 and code < 45) or code == 70:
                    minor_violations_count += 1
            return [
                minor_violations_count, serious_violations_count,
                critical_violations_count
            ]
        else:
            for violation in x:
                if 'PRIORITY VIOLATION' in violation:
                    critical_violations_count += 1
                elif 'PRIORITY FOUNDATION VIOLATION' in violation:
                    serious_violations_count += 1
                elif 'CORE VIOLATION' in violation:
                    minor_violations_count += 1
            return [
                minor_violations_count, serious_violations_count,
                critical_violations_count
            ]


food_data['violations_list'] = food_data.apply(lambda x: count_violations(x),
                                               axis=1)
food_data['minor_violations'] = food_data['violations_list'].apply(
    lambda x: x[0])
food_data['serious_violations'] = food_data['violations_list'].apply(
    lambda x: x[1] if len(x) > 1 else 0)
food_data['critical_violations'] = food_data['violations_list'].apply(
    lambda x: x[2] if len(x) > 1 else 0)
food_data['CriticalFound'] = food_data['critical_violations'].apply(
    lambda x: 1 if x > 0 else 0)


plt.figure(figsize=(12, 6))
food_data[food_data['CriticalFound'] == 0]['inspection_date'].hist(
    bins=29, label="No Critical Violations")
food_data[food_data['CriticalFound'] == 1]['inspection_date'].hist(
    bins=29, label="Found Critical Violations")
plt.xlabel("Inspection Date")
plt.legend(loc='best')
plt.show()

plt.figure(figsize=(12, 16))
ax = sns.countplot(y="neighborhood", hue='CriticalFound',data=food_data)
plt.title("Insepections by neighborhood")
plt.xticks(rotation=30)
plt.show()


per_day = pd.DataFrame()
per_day = food_data[['inspection_date', 'inspection_id']]
per_day = per_day.set_index(pd.to_datetime(per_day['inspection_date']))
per_day = per_day.resample('W').count()
plt.rcParams['figure.figsize'] = 12, 5
fig, ax = plt.subplots()
fig.autofmt_xdate()
#ax.xaxis.set_minor_locator(locator)
ax.xaxis.set_major_locator(mdates.MonthLocator())
#ax.xaxis.set_minor_locator(mdates.DayLocator())
monthFmt = mdates.DateFormatter('%Y-%b')
ax.xaxis.set_major_formatter(monthFmt)

plt.plot(per_day.index, per_day, 'b-')
plt.xlabel('Inspection Date')
plt.ylabel('Number of Inspections')
plt.title('Weekly Inspections')
plt.show()

print("%s unique facilites were inspected during the period" % food_data['license'].nunique())

# Let's drop some redundant and unnecessary columns.

food_data = food_data.drop(['violations_list', 'violations'], axis=1)

# ## Let's look at the results of these inspection more closely: 
# A facility can either pass, pass with conditions or fail. Following is an excerpt from the dataset documentation page:
# 
# "Establishments receiving a ‘pass’ were found to have no critical or serious violations (violation number 1-14 and 15-29, respectively). Establishments receiving a ‘pass with conditions’ were found to have critical or serious violations, but these were corrected during the inspection. Establishments receiving a ‘fail’ were found to have critical or serious violations that were not correctable during the inspection. An establishment receiving a ‘fail’ does not necessarily mean the establishment’s licensed is suspended. Establishments found to be out of business or not located are indicated as such".
print(food_data['results'].value_counts())

ax = sns.countplot(x="results", data=food_data)
plt.title("Result of Inspections")
plt.show()


# Let's convert results in to categorical variable first and the we will filter out non-relevant categories like 'Out of Business', 'Not Ready' and 'No Entry' facilities. 

results_conv = {"results": {
        "Fail": 0,
        "Pass": 1,
        "Pass w/ Conditions": 1,
        "Out of Business": 2,
        "No Entry": 3,
        "Not Ready": 4,
        'Business Not Located': 5
    }
}
food_data.replace(results_conv, inplace=True)
#food_data['results'] = food_data['results'].astype('int')
print(food_data.results.dtype)

food_data.results.value_counts()

# keep only the ones that either passed or failed the inspection
food_data = food_data[food_data['results'] < 2]
ax = sns.countplot(x="CriticalFound", data=food_data)
plt.title("Result of Inspections")
plt.show()

ax = sns.countplot(x="critical_violations", hue='results', data=food_data)
plt.title("Distribution of Serious Violations")
plt.show()

ax = sns.countplot(x="serious_violations", hue='results', data=food_data)
plt.title("Distribution of Serious Violations")
plt.show()

ax = sns.countplot(x="minor_violations", hue='results', data=food_data)
plt.title("Distribution of Serious Violations")
plt.show()


# ##  Inspection type: 
# According to the dataset description, an inspection can be of the following types:
# 
# 1) Canvass : The most common type of inspection performed at a frequency relative to the risk of the establishment
# 
# 2) Consultation: when the inspection is done at the request of the owner prior to the opening of the establishment
# 
# 3) Complaint: when the inspection is done in response to a complaint against the establishment
# 
# 4) license : when the inspection is done as a requirement for the establishment to receive its license to operate
# 
# 5) suspect food poisoning : when the inspection is done in response to one or more persons claiming to have gotten ill as a result of eating at the establishment (a specific type of complaint based inspection)
# 
# 6) Task-force inspection: when an inspection of a bar or tavern is done.
# 
# 7) Re-inspections:  Occurs for most types of these inspections and are indicated as such.


plt.figure(figsize=(10, 6))
ax = sns.countplot(y="inspection_type", data=food_data)
plt.title("Result of Inspections")
plt.show()

food_data = food_data[food_data['inspection_type'] == 'Canvass']

print(
    "%d different types of food establishment facilities were inspected during the period and %d different types of inpsections were conducted during the period."
    % (food_data['facility_type'].nunique(),
       food_data['inspection_type'].nunique()))

food_data['facility_type'].value_counts()[0:10]

# Setting anything other than Restaurants, Grocery store and School to other types
ftype = lambda x: "Other" if x not in [
    'Restaurant', 'Grocery Store', 'School'
] else x
plt.figure(figsize=(12, 6))
food_data['facility_type'] = food_data['facility_type'].map(ftype)
ax = sns.countplot(y="facility_type", data=food_data)
plt.title("Types of Facilities Inspected")
plt.show()

## keeping only th restaurants and grocery store 
food_data = food_data[(food_data['facility_type'] == 'Restaurant') |
                      (food_data['facility_type'] == 'Grocery Store')]
food_data.sort_values(by='inspection_date', inplace=True)


# ### Risk categories: 
#     
# Each establishment is categorized as to its risk of adversely affecting the public’s health:
# 
#  1: High
# 
#  2: Medium 
# 
#  3: Low 
# 
# The frequency of inspection is tied to this risk, with risk 1 establishments inspected most frequently and risk 3 least frequently.

food_data['risk'].value_counts()[0:10]

plt.figure(figsize=(12, 8))
ax = sns.countplot(y="risk", data=food_data)
plt.title("Risk")
plt.show()


# ## Label Encoding categorical variables:
# 
# There are couple different ways of label encoding categorical variables.
# 
# 1) First method is to replace those variables with a dictionary involving key and value pairs of the variables to be encoded. 
# 
# 2) Another method is to change their type as categorical variable. Let's convert inspection_type for example as as categorical variable. 

food_data["facility_type"] = food_data["facility_type"].astype('category')
food_data["risk"] = food_data["risk"].astype('category')
#food_data["inspection_type_cat"] = food_data["inspection_type"].cat.codes
food_data["facility_type_cat"] = food_data["facility_type"].cat.codes
food_data["risk_type_cat"] = food_data["risk"].cat.codes


# I want to see look these establishments in the map. For plotting, let's divide them into pass and fail data frames.
pass_inspection = food_data[(food_data['CriticalFound'] == 0)]
fail_inspection = food_data[food_data['CriticalFound'] == 1]

import gmaps
APIKEY= os.getenv('GMAPAPIKEY')
gmaps.configure(api_key=APIKEY)

def make_heatmap(locations, weights=None):
    fig = gmaps.figure()
    heatmap_layer = gmaps.heatmap_layer(locations)
    heatmap_layer.max_intensity = 100
    heatmap_layer.point_radius = 8
    fig.add_layer(heatmap_layer)
    return fig
locations = zip(food_data['latitude'], food_data['longitude'])
fig = make_heatmap(locations)

## Let's utilize plotly and mapbox to display these restaurants in a map:
import plotly as py
import plotly.graph_objs as go
py.offline.init_notebook_mode()
py.tools.set_credentials_file(username='dipakrimal',
                                  api_key='0d7jgOoPDZTZV2J0l5u4')
mapbox_access_token = os.getenv('MAPBOX_ACCESS_TOKEN')

data_pass = [
    go.Scattermapbox(lat=fail_inspection['latitude'],
                     lon=fail_inspection['longitude'],
                     mode='markers',
                     marker=go.scattermapbox.Marker(size=8,
                                                    color='rgb(255, 0, 0)',
                                                    opacity=0.5),
                     text=fail_inspection['dba_name'] + ' <br> Fail ',
                     hoverinfo='text'), 
    go.Scattermapbox(lat=pass_inspection['latitude'],
                     lon=pass_inspection['longitude'],
                     mode='markers',
                     marker=go.scattermapbox.Marker(size=8,
                                                    color='rgb(50, 150, 50)',
                                                    opacity=0.3),
                     text=pass_inspection['dba_name'] + ' <br> Pass ',
                     hoverinfo='text')
]

layout = go.Layout(
    title="Chicago Food Insepections",
    width=800,
    height=600,
    showlegend=False,
    hovermode='closest',
    mapbox=go.layout.Mapbox(accesstoken=mapbox_access_token,
                            bearing=0,
                            center=go.layout.mapbox.Center(lat=41.9,
                                                           lon=-87.7),
                            pitch=10,
                            zoom=9,
                            style='outdoors'),
)

fig = go.Figure(data=data_pass, layout=layout)

py.offline.iplot(fig, filename='Chicago')

food_data = food_data.set_index(['license', 'event_date'])
food_data.sort_values(by=['license', 'inspection_date'],
                          ascending=[True, False],
                          inplace=True)

food_data['failed'] = food_data['results'].apply(lambda x: 1 if x == 0 else 0)
food_data['past_fail'] = food_data['failed'].shift(-1).fillna(0)
food_data['past_critical_violations'] = food_data['critical_violations'].shift(
    -1).fillna(0)
food_data['past_serious_violations'] = food_data['serious_violations'].shift(
    -1).fillna(0)
food_data['past_minor_violations'] = food_data['minor_violations'].shift(
    -1).fillna(0)
food_data['time_since_last_inspection'] = food_data['inspection_date'].dt.date.diff(
).dt.days.fillna(0).shift(-1) / 365.0
food_data['time_since_last_inspection'].fillna(2, inplace=True)
food_data = food_data.reset_index()
food_data = food_data.drop_duplicates(subset='license', keep='first')

def location_api(df, amenity, radius, apikey):
    amenity_count = []
    for i in range(len(df)):
        count = 0
        #print(df[i], df['longitude'][i])
        url = 'https://us1.locationiq.com/v1/nearby.php?key=' + apikey + '&lat=' + str(
            df.iloc[i]['latitude']) + '&lon=' + str( df.iloc[i]['longitude']) + '&tag=' + amenity + '&radius=' + radius + '&format=json'
        r = requests.get(url)
        data = r.json()
        if 'error' in data:
            amenity_count.append(0)
            #print(data)
            time.sleep(1)
        else:
            count = len(data)
            #print(count)
            #print(i)
            amenity_count.append(count)
            time.sleep(1)

    df[amenity + '_count'] = amenity_count
    return df

food_data = location_api(food_data, 'railway_station', '800', private_token)
food_data = pd.read_csv('../data/processed/food_data_processed.csv')

food_data.to_csv('../data/processed/food_data_processed.csv')