import httpx
import pandas as pd
import asyncio
import os
import io
import numpy as np
from myhttpxlib import make_request
async def B_download_instruments(client,url) -> pd.DataFrame:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Referer": f"{url}", "Upgrade-Insecure-Requests": "1", "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "same-site", "Sec-Fetch-User": "?1", "Te": "trailers"}
    response = await make_request(client,"GET",url, headers=headers)
    data = response.content.decode('utf-8')
    df = pd.read_csv(io.StringIO(data))
    return df

async def split_save():
    B_instrument_download_url1 = os.environ["B_INSTRUMENT_DOWNLOAD_URL1"]
    B_instrument_download_url2 = os.environ["B_INSTRUMENT_DOWNLOAD_URL2"]
    async with httpx.AsyncClient() as client:
        tasks = [
            B_download_instruments(client,B_instrument_download_url1),
            B_download_instruments(client,B_instrument_download_url2)]
        dfs = await asyncio.gather(*tasks)
        df1, df2 = dfs
    combined_df = pd.concat([df1, df2])
    split_dfs = np.array_split(combined_df, 19)
    for i, df in enumerate(split_dfs, 1):
        df.to_csv(f"B_instruments_{i}.csv", index=False)

async def main():
    await split_save()

if __name__ == "__main__":
    asyncio.run(main())