#!/usr/bin/env python

# make sure to install these packages before running:
# pip install pandas
# pip install sodapy

import pandas as pd
from sodapy import Socrata
import datetime
import os
MAXRECORD = 100
import click

@click.command()
@click.option('--startdate', default='2016-12-20', help='start date')

def main(startdate):
    # Unauthenticated client only works with public data sets.
    # SODAPYAPPTOKEN exists in defined in local bash_profile
    app_token = os.environ.get("SODAPYAPPTOKEN")
    client = Socrata("data.cityofchicago.org", app_token)
    download_food_inspections(client, startdate)
    download_crime_data(client, startdate)
    download_service_request_data_after_july01_2018(client)
    download_service_request_data_before_july01_2018(client, startdate)
    download_business_data(client, startdate)
    client.close()

def download_food_inspections(client, startdate):
    dataset_identifier = "cwig-ma7x"
    dataset_filter = "inspection_date>'%s'" %startdate
    # Returned as JSON from API / converted to Python list of dictionaries by sodapy.
    results = client.get(dataset_identifier, where=dataset_filter, limit=MAXRECORD)
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    results_df.to_json('../../data/raw/food-inspection_test.json')

def download_crime_data(client, startdate):
    dataset_identifier = "6zsd-86xi"
    dataset_filter = "primary_type = 'BURGLARY' and date>'%s'" %startdate
    # Returned as JSON from API / converted to Python list of dictionaries by sodapy.
    results = client.get(dataset_identifier, where=dataset_filter, limit=MAXRECORD)
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    results_df.to_json('../../data/raw/burglary_test.json')
    #client.close()

def download_service_request_data_after_july01_2018(client):
    dataset_identifier = "v6vf-nfxy"
    dataset_filter = "sr_type IN ('Garbage Cart Maintenance', 'Sanitation Code Violation', 'Sewer Cleaning Inspection Request', 'Rodent Baiting/Rat Complaint') and created_date > '2018-07-01'"
    # Returned as JSON from API / converted to Python list of dictionaries by sodapy.
    #print(dataset_filter)
    results = client.get(dataset_identifier, where=dataset_filter, limit=MAXRECORD)
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    results_df.to_json('../../data/raw/servicedata_test.json')


def download_service_request_data_before_july01_2018(client, startdate):
    dataset_names = ['garbage', 'sanitation', 'rodent']
    dataset_identifiers = ["9ksk-na4q", "me59-5fac", "97t6-zrhs"]
    dataset_filter = where="creation_date > '%s' and creation_date < '2018-07-01'" %startdate
    # Returned as JSON from API / converted to Python list of dictionaries by sodapy.
    for i in range(len(dataset_identifiers)):
        results = client.get(dataset_identifiers[i], where=dataset_filter, limit=MAXRECORD)
        # Convert to pandas DataFrame
        results_df = pd.DataFrame.from_records(results)
        outfile = "../../data/raw/%sdata_prior_to_july2018_test.json" %dataset_names[i]
        results_df.to_json(outfile)

def download_business_data(client, startdate):
    dataset_identifier = "xqx5-8hwx"
    dataset_filter = where="license_start_date > '%s' " %startdate
    # Returned as JSON from API / converted to Python list of dictionaries by sodapy.
    results = client.get(dataset_identifier, where=dataset_filter, limit=MAXRECORD)
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    results_df.to_json('../../data/raw/business_test.json')


if __name__ == '__main__':
    main()
