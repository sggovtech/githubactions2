import os
import httpx
import pandas as pd
import numpy as np
import io
import asyncio

async def download_NSE_instruments(NSE_INIT,NSE_EQUITY) -> pd.DataFrame:
    client = httpx.AsyncClient()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Referer": "https://www.nseindia.com/", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-site", "Sec-Fetch-User": "?1", "Te": "trailers"}
    response = await client.get(NSE_INIT, headers=headers)
    cookies = response.cookies.items()
    cookies = {name: value for name, value in cookies}
    response = await client.get(NSE_EQUITY, headers=headers, cookies=cookies)
    data = response.content.decode('utf-8')
    df = pd.read_csv(io.StringIO(data))
    return df

async def main():
    NSE_INIT = os.environ["NSE_INIT"]
    NSE_EQUITY = os.environ["NSE_EQUITY"]
    df4 = await download_NSE_instruments(NSE_INIT,NSE_EQUITY)
    dfs = np.array_split(df4, 19)
    for i, df in enumerate(dfs, 1):
        df.to_csv(f"N_instruments_{i}.csv", index=False)

if __name__ == "__main__":
    asyncio.run(main())