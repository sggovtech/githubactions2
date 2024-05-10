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
    print("Downloading NSE bulk block data for the date range:", start_date, "to", end_date)
    client = httpx.AsyncClient()
    start_date = start_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://www.nseindia.com/report-detail/display-bulk-and-block-deals", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Te": "trailers"}
    url_init = os.environ["NSE_MAIN"]
    response = await client.get(url_init, headers=headers)
    cookies = response.cookies.items()
    cookies = {name: value for name, value in cookies}
    nse_bulk_url = os.environ["NSE_BULK_DEALS"]
    nse_block_url = os.environ["NSE_BLOCK_DEALS"]
    tasks = [
        make_request(url=f"{nse_bulk_url}?from={start_date}&to={end_date}&csv=true%22", method="GET", headers=headers, cookies=cookies, client=client),
        make_request(url=f"{nse_block_url}?from={start_date}&to={end_date}&csv=true%22", method="GET", headers=headers, cookies=cookies, client=client)
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
    concat_db.dropna(inplace=True)
    concat_db.to_csv('N_bulk_block_deals.csv',index=False)
    return len(concat_db)

async def submit_NSE_bulk_block_data():
    """
    Submits the NSE bulk block data to the database.
    """
    csv_file = 'N_bulk_block_deals.csv'
    # Upload the CSV file
    
    with open(csv_file, 'rb') as file:
        url = os.environ['BLOCK_SUBMIT_URL']
        headers = {'X-BEARER':os.environ["JWT_SECRET"]}
        attempts = 5
        while attempts > 0:
            attempts -= 1
            try:
                response = httpx.post(url, files={'file': file}, headers=headers)
                break
            except Exception as e:
                print(f"Error: {e} Retrying...")
                continue
        
    # Check the response status
    if response.status_code == 200 and response.json().get('message') == 'Task Initiated':
        print("CSV file uploaded successfully.")
    else:
        print(response.status_code)
        print(response.text)
        print("Failed to upload CSV file.")

async def get_latest_dates():
    """
    Fetches the latest date from the database.
    """
    async with httpx.AsyncClient() as client:
        response = await make_request(client=client,url="https://backend.tradeaajka.com/stock_data/search_block_deals",json_data={"skip": 0,"limit": 1},method="POST",headers={"X-BEARER":os.environ["JWT_SECRET"]},limit=100)
        print(response)
        if response.status_code == 200 and response.json().get('count')==0: # case when no data is present in the database
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
            return start_date, end_date
        elif response.status_code == 200 and response.json().get('count')>0:
            deals = response.json().get('deals')
            last_date = datetime.datetime.strptime(deals[0].get('date'), '%d-%b-%y').date()
            start_date = last_date - datetime.timedelta(days=3)
            end_date = datetime.date.today()
            return start_date, end_date    
    
if __name__ == "__main__":
    if len(sys.argv) == 3:
        start_date = datetime.datetime.strptime(sys.argv[1], '%d-%m-%Y').date()
        end_date = datetime.datetime.strptime(sys.argv[2], '%d-%m-%Y').date()
        len_db = asyncio.run(download_NSE_bulk_block_data(start_date, end_date))
        if len_db>0:
            asyncio.run(submit_NSE_bulk_block_data())
        else:
            print("No data found for the given date range.")
    elif len(sys.argv) == 1:
        start_date,end_date = asyncio.run(get_latest_dates())
        len_db = asyncio.run(download_NSE_bulk_block_data(start_date=start_date, end_date=end_date))
        if len_db>0:
            asyncio.run(submit_NSE_bulk_block_data())
        else:
            print("No data found for the given date range.")
