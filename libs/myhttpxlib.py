import httpx
import traceback
async def make_request(client:httpx.AsyncClient,method:str,url,headers=None,data=None,follow_redirects=True,json_data=None,cookies=None):
    while True:
        try:
            response = await client.request(method, url, headers=headers, data=data, follow_redirects=follow_redirects, json=json_data, cookies=cookies)
            return response
        except httpx.ReadTimeout:
            print("ReadTimeout")
            client.cookies.clear()
            pass
        except httpx.NetworkError:
            print("NetworkError")
            client.cookies.clear()
            pass
        except httpx.ConnectTimeout:
            print("ConnectTimeout")
            client.cookies.clear()
            pass
        except httpx.HTTPStatusError:
            print("HTTPStatusError")
            client.cookies.clear()
            pass
        except httpx.RequestError:
            print("RequestError")
            client.cookies.clear()
            pass
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return None