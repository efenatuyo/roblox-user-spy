import aiohttp

from .. import database

async def get_currently_wearing(session, user_id, proxy):
    async with session.get(f"https://avatar.roblox.com/v1/users/{user_id}/currently-wearing", proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            return False
        if response.status == 200:
            return (await response.json())["assetIds"]

async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            currently_wearing = await get_currently_wearing(session, user_id, proxy)
            if not currently_wearing: continue
            data = database.read()
            if user_id not in data["wearing"]:
                data["wearing"][user_id] = currently_wearing
                database.write(data)
                continue
            for wearing in currently_wearing:
                if wearing not in data["wearing"][user_id]:
                    embed_data = {"embeds": [{"title": "User Tracker | New Asset Wearing", "fields": [{"name": "Asset Link", "value": f"[Asset](https://www.roblox.com/catalog/{wearing})", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["wearing"][user_id].append(wearing)
                    database.write(data)
            for wearing in data["wearing"][user_id].copy():
                if wearing not in currently_wearing:
                    embed_data = {"embeds": [{"title": "User Tracker | New Asset Not Wearing", "fields": [{"name": "Asset Link", "value": f"[Asset](https://www.roblox.com/catalog/{wearing})", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["wearing"][user_id].remove(wearing)
                    database.write(data)
                        
        except Exception as e:
            print("ERROR: " + str(e))