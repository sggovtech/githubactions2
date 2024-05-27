import pandas as pd
import datetime
import requests
import io
from bs4 import BeautifulSoup
import sys
import asyncio
import os
import httpx
from libs.myhttpxlib import make_request


async def get_hidden_input(content):
    """ Return the dict contain the hidden input 
    """
    tags = dict()
    soup =BeautifulSoup(content, 'html.parser')
    hidden_tags = soup.find_all('input', type='hidden')
    for tag in hidden_tags:
        try:
            name = tag.get('name')
            value = tag.get('value')
            if value is not None or value != '':
                tags[name] = value
            else:
                tags[name] = ''
        except Exception as e:
            continue
    return tags

async def download_BSE_bulk_block_data(start_date:datetime.datetime.date, end_date:datetime.datetime.date) -> int:
    """
    Requests BSE (Bombay Stock Exchange) data for a given date range.
    
    Args:
        start_date (str): The start date in the format "dd-mm-yyyy".
        end_date (str): The end date in the format "dd-mm-yyyy".
    
    Returns:
        pd.Dataframe : Pandas Dataframe.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.bseindia.com", "Referer": "https://www.bseindia.com/markets/equity/eqreports/bulknblockdeals.aspx", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "Te": "trailers"}
    url = os.environ['BSE_BULK_DEALS']
    response = requests.get(url, headers=headers)
    hidden = await get_hidden_input(response.content)
    values = {
        'ctl00$ContentPlaceHolder1$rblDT': 1,
        'ctl00$ContentPlaceHolder1$chkAllMarket':'on',
        'ctl00$ContentPlaceHolder1$txtDate':start_date.strftime('%d/%m/%Y'),
        'ctl00$ContentPlaceHolder1$txtToDate':end_date.strftime('%d/%m/%Y')
    }
    join_hidden = {**hidden, **values}
    join_hidden['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$btnDownload'
    response = requests.post(url, headers=headers, data=join_hidden)
    data = response.content.decode('utf-8')
    if "<!DOCTYPE html>" in data:
        print("No Data")
        df= pd.DataFrame()
    else:
        df = pd.read_csv(io.StringIO(data),index_col=False)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.bseindia.com", "Referer": "https://www.bseindia.com/markets/equity/eqreports/bulknblockdeals.aspx", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "Te": "trailers"}
    response = requests.get(url, headers=headers)
    hidden = await get_hidden_input(response.content)
    values = {
        'ctl00$ContentPlaceHolder1$rblDT': 2,
        'ctl00$ContentPlaceHolder1$chkAllMarket':'on',
        'ctl00$ContentPlaceHolder1$txtDate':start_date.strftime('%d/%m/%Y'),
        'ctl00$ContentPlaceHolder1$txtToDate':end_date.strftime('%d/%m/%Y')
    }
    join_hidden = {**hidden, **values}
    join_hidden['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$btnDownload'
    response = requests.post(url, headers=headers, data=join_hidden)
    data = response.content.decode('utf-8')
    if "<!DOCTYPE html>" in data:
        print("No Data")
        df2= pd.DataFrame()
    else:
        df2 = pd.read_csv(io.StringIO(data),index_col=False)
    concat_db = pd.concat([df, df2])
    new_column_names  = ['Date','BSE_Code','Symbol','Client_Name','Deal_Type','Quantity_Traded','Price']
    concat_db.columns = new_column_names
    concat_db['Deal_Type'] = concat_db['Deal_Type'].replace({'P': 'BUY', 'S': 'SELL'})
    concat_db['Quantity_Traded'] = concat_db['Quantity_Traded'].astype(int)
    concat_db['Price'] = concat_db['Price'].astype(float)
    concat_db.drop_duplicates(subset=['Date','BSE_Code','Symbol','Client_Name','Deal_Type','Quantity_Traded','Price'],inplace=True)
    concat_db["Remarks"] = "-"
    concat_db.dropna(inplace=True)
    concat_db.to_csv('B_bulk_block_deals.csv',index=False)
    return len(concat_db)

async def submit_BSE_bulk_block_data():
    """
    Submits the NSE bulk block data to the database.
    """
    csv_file = 'B_bulk_block_deals.csv'
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
        len_db = asyncio.run(download_BSE_bulk_block_data(start_date, end_date))
        if len_db>0:
            asyncio.run(submit_BSE_bulk_block_data())
        else:
            print("No data found for the given date range.")
    elif len(sys.argv) == 1:
        start_date,end_date = asyncio.run(get_latest_dates())
        len_db = asyncio.run(download_BSE_bulk_block_data(start_date=start_date, end_date=end_date))
        if len_db > 0:
            asyncio.run(submit_BSE_bulk_block_data())
        else:
            print("No data found for the given date range.")
