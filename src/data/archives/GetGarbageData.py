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

# Example authenticated client (needed for non-public datasets):

# First 2000 results, returned as JSON from API / converted to Python list of
# dictionaries by sodapy.
#results = client.get("9ksk-na4q", where="sr_type IN ('Garbage Cart Maintenance', 'Sanitation Code Violation', 'Sewer Cleaning Inspection Request', 'Rodent Baiting/Rat Complaint') and created_date > '2016-12-20'", limit=20000000)
results = client.get("me59-5fac", where="creation_date > '2016-12-20' and creation_date < '2018-07-02'", limit=200000)

# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
#results_df = results_df[results_df['']
results_df.to_json("../../data/raw/sanitation_prior_to_july2018.json")
