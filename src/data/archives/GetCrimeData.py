#!/usr/bin/env python

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata

# Unauthenticated client only works with public data sets. Note 'None'
# in place of application token, and no username or password:
client = Socrata("data.cityofchicago.org",
                 "yEuRuEw33uYK8NCFXRfaE2wsO",
                 username="rimaldipak@gmail.com",
                 password="Fiu$33199")

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
query = "6zsd-86xi"

results = client.get(query, where="primary_type = 'BURGLARY' and date > '2016-12-20'", limit=200000)

# Convert to pandas DataFrame
#results_df = results_df[results_df['primary_type']=='BURGLARY']
results_df = pd.DataFrame.from_records(results)
results_df.to_json("burglary.json")
