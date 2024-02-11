import asyncio
import requests
import ssl
import certifi
import websockets

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

def get_ws_url():
    r = requests.post('https://api.kucoin.com/api/v1/bullet-public')
    data = r.json()["data"]
    token = data["token"]
    endpoint = data['instanceServers'][0]['endpoint']

    ws_url = f"{endpoint}/?token={token}"

    return ws_url

def ws_conn(url):
    print(url)
    with connect(url, ssl=ssl_context) as websocket:
      websocket.send("Hello world!")
      message = websocket.recv()
      print(f"Received: {message}")


async def main():
    ws_url = get_ws_url()
    async with websockets.connect(ws_url, ssl=ssl_context) as ws:
        response = await ws.recv()
        print(response)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
