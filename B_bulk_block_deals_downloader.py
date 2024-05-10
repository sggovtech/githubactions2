import pandas as pd
import datetime
import requests
import io
from bs4 import BeautifulSoup


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

async def download_BSE_bulk_block_data(start_date:datetime.datetime.date, end_date:datetime.datetime.date) -> pd.DataFrame:
    """
    Requests BSE (Bombay Stock Exchange) data for a given date range.
    
    Args:
        start_date (str): The start date in the format "dd-mm-yyyy".
        end_date (str): The end date in the format "dd-mm-yyyy".
    
    Returns:
        pd.Dataframe : Pandas Dataframe.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.bseindia.com", "Referer": "https://www.bseindia.com/markets/equity/eqreports/bulknblockdeals.aspx", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "Te": "trailers"}
    url = f"https://www.bseindia.com/markets/equity/eqreports/bulknblockdeals.aspx"
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
    return concat_db

