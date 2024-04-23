import pandas as pd
import glob
import httpx
import os
import asyncio
from libs.myhttpxlib import make_request

async def submit_data(client:httpx.Client,json_data:dict) -> str:
    url = os.environ['SUBMIT_URL']
    headers = {'X-BEARER':os.environ["JWT_SECRET"]}
    response = await make_request(url=url, json=json_data, headers=headers, client=client, method="POST")
    return response.text

async def main():
    # Get a list of all CSV files in the directory
    csv_files = glob.glob('B_instruments*.csv')

    # Create an empty list to store the dataframes
    dfs = []

    # Read each CSV file and append its contents to the list
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)

    # Concatenate the dataframes into one
    combined_df = pd.concat(dfs)

    # Save the combined dataframe to a new CSV file
    combined_df.to_csv('combined_instruments.csv', index=False)
   

if __name__ == "__main__":
    asyncio.run(main())