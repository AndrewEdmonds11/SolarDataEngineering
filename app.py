import streamlit as st
import boto3
from dotenv import load_dotenv
import os
import time
import src.transform_solar as transform_solar
import pandas as pd
import plotly.express as px

st.title("Solar Data Explorer :sunny:")
st.write("Hello World! :sunny:")

# Load variables from the .env file into os.environ
load_dotenv()

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define your bucket and file path (key)
bucket_name = os.getenv("S3_BUCKET_NAME")
file_key = 'solar_data.csv'

start_time = time.time()
        
# Fetch the object from S3
file_content = "Failure"
with st.spinner("Processing large dataset... Please wait."):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    # Calculate final elapsed time
    elapsed_time = time.time() - start_time

    st.write(f"File content fetched from S3 in {elapsed_time:.2f} seconds.")

    file_content = response['Body'].read().decode('utf-8')

df = transform_solar.process_raw_data(file_content)

fig = px.line(df.groupby(df['timestamp'].dt.date).agg({'DHI': 'mean'}), y='DHI', title='Daily Mean Direct Horizontal Irradiance (DHI) [W/m^2]]')
fig.update_yaxes(rangemode="tozero")
st.plotly_chart(fig)