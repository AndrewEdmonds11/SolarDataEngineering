import os
from dotenv import load_dotenv
import requests
import pandas as pd
import boto3

import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def upload_to_s3(local_file_path, bucket_name, s3_object_name=None):
    """
    Uploads a local file to an AWS S3 bucket.
    """
    # If S3 object_name was not specified, use the local file name
    if s3_object_name is None:
        import os
        s3_object_name = os.path.basename(local_file_path)

    # Initialize the S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the file
        s3_client.upload_file(local_file_path, bucket_name, s3_object_name)
        print(f"Successfully uploaded {local_file_path} to {bucket_name}/{s3_object_name}")
        return True
    except FileNotFoundError:
        print(f"The file {local_file_path} was not found.")
        return False
    except NoCredentialsError:
        print("AWS credentials not found. Please configure your AWS environment.")
        return False
    except ClientError as e:
        print(f"An error occurred: {e}")
        return False

def fetch_nsrdb_data(longitude, latitude):
    """
    Fetches solar data from the NSRDB API for the given longitude and latitude.
    """
    # Load variables from the .env file into os.environ
    load_dotenv()

    # Access the environment variable
    nsrdb_key = os.getenv("NSRDB_KEY")
    email = os.getenv("EMAIL")

    url = "https://developer.nlr.gov/api/nsrdb/v2/solar/nsrdb-GOES-conus-v4-0-0-download.csv?api_key="+nsrdb_key 

    payload = {
        'api_key': nsrdb_key,
        'wkt': f'POINT({longitude:.2f} {latitude:.2f})',
        'attributes': 'dhi',
        'names': '2018',
        'utc': 'false',
        'email': email,
        'interval': '60',
        'leap_day': 'true'
    }
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    if response.status_code != 200:
        print(f"Error occurred while fetching data: {response.status_code}")
        print(f"Error details: {response.text}")
        return None

    filename = f'solar_data_{longitude:.2f}_{latitude:.2f}.csv'
    with open('test-data/solar_data.csv', 'w') as f: # put in temporary location
        f.write(response.text)

    upload_to_s3('test-data/solar_data.csv', os.getenv("S3_BUCKET_NAME"), filename)