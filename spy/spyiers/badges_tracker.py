import aiohttp

from .. import database

async def get_badges(session, user_id, proxy):
    async with session.get(f"https://www.roblox.com/users/inventory/list-json?assetTypeId=21&cursor=&itemsPerPage=200&pageNumber=1&userId={user_id}", proxy=proxy.current) as response:    # TODO: make it get all badges instead of just 100
        if response.status == 429:
            proxy.next()
            return False
        if response.status == 200:
            return (await response.json())["Data"]["Items"]

async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            badges = await get_badges(session, user_id, proxy)
            if not badges: continue
            data = database.read()
            if user_id not in data["badges"]:
                data["badges"][user_id] = {}
                for badge in badges:
                    data["badges"][user_id][str(badge["Item"]["AssetId"])] = badge
                database.write(data)
                continue
            for badge in badges:
                if str(badge["Item"]["AssetId"]) not in data["badges"][user_id]:
                    embed_data = {"embeds": [{"title": "User Tracker | Badge Added", "fields": [{"name": "Badge Link", "value": f"[Badge](https://www.roblox.com/badges/{str(badge['Item']['AssetId'])}/xolo)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["badges"][user_id][str(badge["Item"]["AssetId"])] = badge
                    database.write(data)
            all_badges = []
            for badge in badges:
                all_badges.append(str(badge["Item"]["AssetId"]))
            for badge in data["badges"][user_id].copy():
                if badge not in all_badges:
                    embed_data = {"embeds": [{"title": "User Tracker | Badge Removed", "fields": [{"name": "Badge Link", "value": f"[Badge](https://www.roblox.com/badges/{badge}/xolo)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    # await session.post(self.config['webhook'], json=embed_data) this does not work due to get_badges only fetching currently 100 badges so if a new badge gets added one badge will get invisible (old)
                    del data["badges"][user_id][badge]
                    database.write(data)
                        
        except Exception as e:
            print("ERROR: " + str(e))