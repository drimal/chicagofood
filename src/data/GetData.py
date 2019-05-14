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
results = client.get("cwig-ma7x", where="inspection_date > '2018-01-01'", limit=2000000)
# Convert to pandas DataFrame
results_df = pd.DataFrame.from_records(results)
results_df.to_json("../data/food-inspection.json")
