import pandas as pd
import glob
import httpx
import os
import asyncio
from libs.myhttpxlib import make_request
import requests

async def submit_data(client:httpx.Client,json_data:dict) -> str:
    url = os.environ['INSTRUMENT_SUBMIT_URL']
    headers = {'X-BEARER':os.environ["JWT_SECRET"]}
    response = await make_request(url=url, json_data=json_data, headers=headers, client=client, method="POST")
    return await response.text


async def main():
    # Read the CSV file
    csv_file = 'combined_instruments.csv'
    
    # Upload the CSV file
    with open(csv_file, 'rb') as file:
        url = os.environ['INSTRUMENT_SUBMIT_URL']
        headers = {'X-BEARER':os.environ["JWT_SECRET"]}
        response = requests.post(url, files={'file': file}, headers=headers)
    
    # Check the response status
    if response.status_code == 200:
        print("CSV file uploaded successfully.")
    else:
        print(response.status_code)
        print(response.text)
        print("Failed to upload CSV file.")

if __name__ == "__main__":
    asyncio.run(main())