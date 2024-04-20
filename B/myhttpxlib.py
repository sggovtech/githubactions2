import httpx
import traceback
async def make_request(client:httpx.AsyncClient,method:str,url,headers=None,data=None):
    while True:
        try:
            response = await client.request(method, url, headers=headers,data=data)
            return response
        except httpx.ReadTimeout:
            client.cookies.clear()
            pass
        except httpx.NetworkError:
            client.cookies.clear()
            pass
        except httpx.ConnectTimeout:
            client.cookies.clear()
            pass
        except httpx.HTTPStatusError:
            client.cookies.clear()
            pass
        except httpx.RequestError:
            client.cookies.clear()
            pass
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
            return None