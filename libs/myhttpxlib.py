import httpx
import traceback
async def make_request(client:httpx.AsyncClient,method:str,url,headers=None,data=None,follow_redirects=True,json_data=None,cookies=None,limit=100_00):
    while limit > 0:
        limit -= 1
        try:
            response = await client.request(method, url, headers=headers, data=data, follow_redirects=follow_redirects, json=json_data, cookies=cookies)
            return response
        except httpx.ReadTimeout:
            print("ReadTimeout")
            client.cookies.clear()
            if "nse" in url:
                url_init = "https://www.nseindia.com"
                response = await client.get(url_init, headers=headers)
                cookies = response.cookies.items()
                cookies = {name: value for name, value in cookies}
        except httpx.NetworkError:
            print("NetworkError")
            client.cookies.clear()
            if "nse" in url:
                url_init = "https://www.nseindia.com"
                response = await client.get(url_init, headers=headers)
                cookies = response.cookies.items()
                cookies = {name: value for name, value in cookies}
            pass
        except httpx.ConnectTimeout:
            print("ConnectTimeout")
            client.cookies.clear()
            if "nse" in url:
                url_init = "https://www.nseindia.com"
                response = await client.get(url_init, headers=headers)
                cookies = response.cookies.items()
                cookies = {name: value for name, value in cookies}
            pass
        except httpx.HTTPStatusError:
            print("HTTPStatusError")
            client.cookies.clear()
            if "nse" in url:
                url_init = "https://www.nseindia.com"
                response = await client.get(url_init, headers=headers)
                cookies = response.cookies.items()
                cookies = {name: value for name, value in cookies}
            pass
        except httpx.RequestError:
            print("RequestError")
            client.cookies.clear()
            if "nse" in url:
                url_init = "https://www.nseindia.com"
                response = await client.get(url_init, headers=headers)
                cookies = response.cookies.items()
                cookies = {name: value for name, value in cookies}
            pass
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return None