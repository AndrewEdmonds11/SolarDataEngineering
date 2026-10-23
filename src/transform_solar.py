# import os

# import boto3
# from dotenv import load_dotenv

import pandas as pd
from io import StringIO

# # Load variables from the .env file into os.environ
# load_dotenv()

# # Initialize the S3 client
# s3_client = boto3.client('s3')

# # Define your bucket and file path (key)
# bucket_name = os.getenv("S3_BUCKET_NAME")
# file_key = 'solar_data.csv'

# # Fetch the object from S3
# response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

# file_content = response['Body'].read().decode('utf-8')

def process_raw_data(file_content):
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
    
    df['DHI'] = pd.to_numeric(df['DHI'], errors="coerce"))
    df['GHI'] = pd.to_numeric(df['GHI'], errors="coerce")
    return df # df[(df['DHI']!=0) & (df['DHI'].notnull())] # only return daylight hours

#print(df.head(24))

#import matplotlib.pyplot as plt

#day_strs = ['2018-01-01', '2018-06-01', '2018-12-01']
#for day_str in day_strs:
#    day = pd.to_datetime(day_str)
#    single_day_df = df[df['timestamp'].dt.date == day.date()]
#    plt.plot(single_day_df['timestamp'].dt.hour, single_day_df['DHI'], marker='o', linestyle='-', label=day_str)

##print(single_day_df.head(24))

##print(df.dtypes)

##daytime_df = df[(df['DHI']!=0) & (df['DHI'].notnull())]
##print(daytime_df.head(24))

##grouped_df = daytime_df.groupby(daytime_df['timestamp'].dt.date).agg({'DHI': ['mean', 'std']}).reset_index()
##print(grouped_df.head(10))

#plt.xlabel('Hour of Day')
#plt.ylabel('DHI [W/m^2]')
#plt.title('DHI over Time for a Single Day')
#plt.grid(True)
#plt.legend()
#plt.show()

##plt.hist(df[df['timestamp'].dt.date == df['timestamp'].dt.date.iloc[0]]['DHI'], bins=30, edgecolor='black')
##plt.xlabel('DHI')
##plt.show()

##plt.errorbar(grouped_df['timestamp'], grouped_df[('DHI', 'mean')], yerr=grouped_df[('DHI', 'std')], fmt='.', capsize=2)
##plt.xlabel('timestamp')
##plt.ylabel('DHI')
##plt.title('Solar Data')
##plt.show()