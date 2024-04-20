import asyncio
import httpx
import pandas as pd
import sys
import os
from bs4 import BeautifulSoup
import re
from libs.random_useragent import get_random_user_agent
from libs.myhttpxlib import make_request
async def B_get_hidden_input(content):
    """ Return the dict contain the hidden input 
    """
    tags = dict()
    soup = BeautifulSoup(content, 'html.parser')
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

async def B_shareholding_requester(client:httpx.Client,instrument:dict) -> dict:
    code = instrument['Security Code']
    print(code)
    rand_user_agent = await get_random_user_agent()
    headers = {"User-Agent": rand_user_agent, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.bseindia.com", "Referer": "https://www.bseindia.com/markets/equity/eqreports/bulknblockdeals.aspx", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-User": "?1", "Te": "trailers"}
    url = os.environ["B_SEARCH_CAP"]
    response = await make_request(client,"GET",url,headers=headers)
    hidden = await B_get_hidden_input(response.content)
    values = {
        'ctl00$ContentPlaceHolder1$hdnCode':'',
        'ctl00$ContentPlaceHolder1$industry':'ALL',
        'ctl00$ContentPlaceHolder1$brodcast':'1',
        'ctl00$ContentPlaceHolder1$scrip':code,
        'ctl00$ContentPlaceHolder1$Hidden1':'',
        'ctl00$ContentPlaceHolder1$SmartSearch$hdnCode':code,
        'ctl00$ContentPlaceHolder1$SmartSearch$smartSearch':'',
        'ctl00$ContentPlaceHolder1$hf_scripcode':code,
        'ctl00$ContentPlaceHolder1$ddlbrodcast':7,
        'ctl00$ContentPlaceHolder1$ddlindustry':'ALL',
        'ctl00$ContentPlaceHolder1$btnSubmit':'Submit'
    }
    join_hidden = {**hidden, **values}
    response = await make_request(client,"POST",url,headers=headers,data=join_hidden)
    hidden = await B_get_hidden_input(response.content)
    values = {
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$gvData$ctl02$lnkXML",
                "__EVENTARGUMENT": '', 
                "ctl00$ContentPlaceHolder1$hdnCode": '',
                "ctl00$ContentPlaceHolder1$industry": "ALL",
                "ctl00$ContentPlaceHolder1$brodcast": "7",
                "ctl00$ContentPlaceHolder1$scrip": code,
                "ctl00$ContentPlaceHolder1$Hidden1": '',
                "ctl00$ContentPlaceHolder1$SmartSearch$hdnCode": code,
                "ctl00$ContentPlaceHolder1$SmartSearch$smartSearch": '',
                "ctl00$ContentPlaceHolder1$hf_scripcode": code,
                "ctl00$ContentPlaceHolder1$ddlbrodcast": 7,
                "ctl00$ContentPlaceHolder1$ddlindustry": "ALL"
            }
    join_hidden = {**hidden, **values}
    response = await make_request(client,"POST",url,headers=headers,data=join_hidden,follow_redirects=True)

    if "<xbrli" in response.text:
        num_shares = re.findall(r'<in-bse-shp:NumberOfFullyPaidUpEquityShares contextRef="ShareholdingPattern_ContextI" unitRef="shares" decimals="INF">(\d+)</in-bse-shp:NumberOfFullyPaidUpEquityShares>', response.text)
        if len(num_shares) > 0:
            num_shares = int(num_shares[0])
            instrument["market_cap"] = num_shares
            return instrument
        else:   
            return instrument
    else:
        return instrument


async def shareholding_pattern(file_pattern) -> pd.DataFrame:
    B_file_name = f"B_instruments_{file_pattern}.csv"
    B_data = pd.read_csv(B_file_name)
    B_data["market_cap"] = ""
    B_data = B_data.to_dict(orient='records')

    async with httpx.AsyncClient() as client:
        B_chunks = [B_data[i:i+20] for i in range(0, len(B_data), 20)]
        B_results = []
        for chunk in B_chunks :
            client.cookies.clear()
            tasks = [B_shareholding_requester(client, instrument) for instrument in chunk]
            chunk_results = await asyncio.gather(*tasks)
            B_results.extend(chunk_results)
    return B_results

async def main(arg:str):
    B_data = await shareholding_pattern(arg)
    B_df = pd.DataFrame(B_data)
    B_df.to_csv(f"B_instruments_{arg}.csv", index=False)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))