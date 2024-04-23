import asyncio
import sys
import pandas as pd
import httpx
import os
from libs.myhttpxlib import make_request
import urllib.parse
import json
import re


async def N_shareholding_requester(client:httpx.AsyncClient, instrument:dict) -> dict:
    N_code = instrument['SYMBOL']
    print(N_code)
    N_name = instrument['NAME OF COMPANY']
    NSE_MAIN = os.environ["NSE_MAIN"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Te": "trailers"}
    resp1 = await make_request(url=NSE_MAIN, client=client ,method="GET", headers=headers, follow_redirects=True)
    cookies_dict = {k: v for k, v in resp1.cookies.items()}
    NSE_SHARE_PATTERN = os.environ["NSE_SHARE_PATTERN"]+f"symbol={urllib.parse.quote(N_code,safe='')}&issuer={urllib.parse.quote(N_name, safe='')}"
    resp2 = await make_request(url=NSE_SHARE_PATTERN,method="GET",client=client, headers=headers, cookies=cookies_dict)
    data = json.loads(resp2.text) 
    if len(data) > 0:
        xrbl_url = data[0]['xbrl']
        resp3 = await make_request(url=xrbl_url, method="GET",client=client ,headers=headers, cookies=cookies_dict)
        if "<xbrli" in resp3.text:
            num_shares = re.findall(r'<in-bse-shp:NumberOfFullyPaidUpEquityShares contextRef="ShareholdingPatternI" unitRef="shares" decimals="INF">(\d+)</in-bse-shp:NumberOfFullyPaidUpEquityShares>', resp3.text)
            if len(num_shares) > 0:
                num_shares = int(num_shares[0])
                instrument["market_cap"] = num_shares
                return instrument
            else:
                instrument["market_cap"] = "0"
                return instrument
        else:
            instrument["market_cap"] = "0"
            return instrument
    else:
        instrument["market_cap"] = "0"
        return instrument

async def shareholding_pattern(file_pattern) -> pd.DataFrame:
    N_file_name = f"N_instruments_{file_pattern}.csv"
    N_data = pd.read_csv(N_file_name)
    N_data["market_cap"] = ""
    N_data = N_data.to_dict(orient='records')

    async with httpx.AsyncClient() as client:
        N_chunks = [N_data[i:i+20] for i in range(0, len(N_data), 20)]
        N_results = []
        for chunk in N_chunks :
            client.cookies.clear()
            tasks = [N_shareholding_requester(client, instrument) for instrument in chunk]
            chunk_results = await asyncio.gather(*tasks)
            N_results.extend(chunk_results)
    return N_results

async def main(arg:str):
    N_data = await shareholding_pattern(arg)
    N_df = pd.DataFrame(N_data)
    N_df.to_csv(f"N_instruments_{arg}.csv", index=False)    



if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))