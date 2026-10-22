import streamlit as st
import boto3
import botocore
from dotenv import load_dotenv
import os
import time
import src.transform_solar as transform_solar
from src.ingest_solar_data import fetch_nsrdb_data
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

st.title("Solar Data Explorer :sunny:")
st.write("Hello World! :sunny:")

# Load variables from the .env file into os.environ
load_dotenv()

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define your bucket
bucket_name = os.getenv("S3_BUCKET_NAME")

# Initialize the geocoder with a custom user-agent
geolocator = Nominatim(user_agent="my_streamlit_location_app")

with st.form("fetch_data"):
    # 1. Provide a text field for the address
    address_input = st.text_input(
        "Enter Address, City, or Zip Code:", 
        placeholder="e.g., Chicago"
    )
    submitted = st.form_submit_button("Submit")
if submitted:
    try:
        # Look up the address coordinates
        location = geolocator.geocode(address_input)
            
        if location:
            st.success(f"Location Found: {location.address}")    
            # Extract specific attributes
            lat = location.latitude
            lon = location.longitude
            
            # Display results
            st.metric("Latitude", f"{lat:.5f}")
            st.metric("Longitude", f"{lon:.5f}")

            # See if raw data file already exists in S3
            file_key = f'solar_data_{lon:.2f}_{lat:.2f}.csv'
            st.write(f"Checking for existing data in S3: {file_key}")
            try:
                s3_client.head_object(Bucket=bucket_name, Key=file_key)
                st.success(f"Data for this location already exists in S3: {file_key}")
            
            except botocore.exceptions.ClientError as e:
                st.info(f"Data for this location does not exist in S3. A new file will be created: {file_key}")
                with st.spinner("Fetching data from NSRDB and uploading to S3..."):
                    start_time = time.time()  
                    fetch_nsrdb_data(lon, lat)
                    # Calculate final elapsed time
                    elapsed_time = time.time() - start_time
                    st.write(f"Data fetched from NSRDB and uploaded to S3 in {elapsed_time:.2f} seconds.")

            start_time = time.time()                                           
            # Fetch the object from S3
            file_content = "Failure"
            with st.spinner("Fetching..."):
                response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            
                # Calculate final elapsed time
                elapsed_time = time.time() - start_time
                st.write(f"File content fetched from S3 in {elapsed_time:.2f} seconds.")
            file_content = response['Body'].read().decode('utf-8')
            
            df = transform_solar.process_raw_data(file_content)
            
            fig = px.line(df.groupby(df['timestamp'].dt.date).agg({'DHI': 'mean'}), y='DHI', title=f'Daily Mean Direct Horizontal Irradiance (DHI) [W/m^2] ({address_input})')
            fig.update_yaxes(rangemode="tozero")
            st.plotly_chart(fig)

        else:
                st.error("Could not find that location. Please try a more specific address.")
                
    except GeocoderServiceError:
        st.error("The geocoding service is currently busy or unavailable. Please try again.")