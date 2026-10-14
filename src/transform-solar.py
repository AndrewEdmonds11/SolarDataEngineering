import os

import boto3
from dotenv import load_dotenv

import pandas as pd
from io import StringIO

# Load variables from the .env file into os.environ
load_dotenv()

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define your bucket and file path (key)
bucket_name = os.getenv("S3_BUCKET_NAME")
file_key = 'solar_data.csv'

# Fetch the object from S3
response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

file_content = response['Body'].read().decode('utf-8')

# first two lines are metadata, so skip them for now
df = pd.read_csv(StringIO(file_content), skiprows=2)
# Build a consistent timestamp
df["timestamp"] = pd.to_datetime(
    {
        "year": df["Year"],
        "month": df["Month"],
        "day": df["Day"],
        "hour": df["Hour"],
        "minute": df["Minute"],
    },
    errors="coerce",
)
df['DHI'] = pd.to_numeric(df['DHI'], errors="coerce")
print(df.head(24))

import matplotlib.pyplot as plt
plt.plot(df['timestamp'], df['DHI'], '-')
plt.xlabel('timestamp')
plt.ylabel('DHI')
plt.title('Solar Data')
plt.show()