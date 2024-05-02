import pandas as pd
import datetime
import httpx
import io
import datetime
import asyncio
from libs.myhttpxlib import make_request
import os
import sys

async def download_NSE_bulk_block_data(start_date:datetime.datetime.date, end_date:datetime.datetime.date) -> pd.DataFrame:
    """
    Requests NSE (National Stock Exchange) data for a given date range.
    
    Args:
        start_date (str): The start date in the format "dd-mm-yyyy".
        end_date (str): The end date in the format "dd-mm-yyyy".
    
    Returns:
        pd.Dataframe : Pandas Dataframe.
    """
    client = httpx.AsyncClient()
    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://www.nseindia.com/report-detail/display-bulk-and-block-deals", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}
    url_init = os.environ["NSE_MAIN"]
    response = await client.get(url_init, headers=headers)
    cookies = response.cookies.items()
    cookies = {name: value for name, value in cookies}
    tasks = [
        make_request(url=f"{os.environ["NSE_BULK_DEALS"]}?from={start_date}&to={end_date}&csv=true%22", method="GET", headers=headers, cookies=cookies, client=client),
        make_request(url=f"{os.environ["NSE_BLOCK_DEALS"]}?from={start_date}&to={end_date}&csv=true%22", method="GET", headers=headers, cookies=cookies, client=client)
    ]
    responses = await asyncio.gather(*tasks)
    df = pd.read_csv(io.StringIO(responses[0].text),index_col=False)
    df2 = pd.read_csv(io.StringIO(responses[1].text),index_col=False)
    concat_db : pd.DataFrame = pd.concat([df, df2])
    new_column_names  = ['Date','Symbol','Name','Client_Name','Deal_Type','Quantity_Traded','Price','Remarks']
    concat_db.columns = new_column_names
    # pd.to_datetime(concat_db['Date'],format='%d-%b-%Y',).dt.date
    concat_db['Quantity_Traded'] = concat_db['Quantity_Traded'].str.replace(',', '').astype(int)
    try:
        concat_db['Price'] = concat_db['Price'].str.replace(',', '').astype(float)
    except:
        pass
    concat_db.drop_duplicates(subset=['Date','Symbol','Name','Client_Name','Deal_Type','Quantity_Traded','Price','Remarks'],inplace=True)
    concat_db.to_csv('N_bulk_block_deals.csv',index=False)

async def submit_NSE_bulk_block_data():
    """
    Submits the NSE bulk block data to the database.
    """
    csv_file = 'N_bulk_block_deals.csv'
    # Upload the CSV file
    with open(csv_file, 'rb') as file:
        url = os.environ['BLOCK_SUBMIT_URL']
        headers = {'X-BEARER':os.environ["JWT_SECRET"]}
        response = httpx.post(url, files={'file': file}, headers=headers)
    
    # Check the response status
    if response.status_code == 200 and response.json().get('message') == 'Task Initiated':
        print("CSV file uploaded successfully.")
    else:
        print(response.status_code)
        print(response.text)
        print("Failed to upload CSV file.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        start_date = datetime.datetime.strptime(sys.argv[1], '%d-%m-%Y').date()
        end_date = datetime.datetime.strptime(sys.argv[2], '%d-%m-%Y').date()
        asyncio.run(download_NSE_bulk_block_data(start_date, end_date))
        asyncio.run(submit_NSE_bulk_block_data())
    elif len(sys.argv) == 1:
        asyncio.run(download_NSE_bulk_block_data(datetime.date.today(), datetime.date.today()))
        asyncio.run(submit_NSE_bulk_block_data())
