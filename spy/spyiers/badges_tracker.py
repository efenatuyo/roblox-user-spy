import aiohttp

from .. import database

async def get_badges(session, user_id, proxy):
  cursor = None
  badges = []
  while True:
    async with session.get(f"https://badges.roblox.com/v1/users/{user_id}/badges?sortOrder=Desc&limit=100&cursor={cursor if cursor else ''}", proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            continue
        if response.status == 200:
            json_response = await response.json()
            badges += json_response["data"]
            if json_response["nextPageCursor"]:
                cursor = json_response["nextPageCursor"]
            else:
                return badges

async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            badges = await get_badges(session, user_id, proxy)
            if badges is False: continue
            data = database.read()
            if user_id not in data["badges"]:
                data["badges"][user_id] = {}
                for badge in badges:
                    data["badges"][user_id][str(badge["id"])] = badge
                database.write(data)
                continue
            for badge in badges:
                if str(badge["id"]) not in data["badges"][user_id]:
                    embed_data = {"embeds": [{"title": "User Tracker | Badge Added", "fields": [{"name": "Badge Link", "value": f"[Badge](https://www.roblox.com/badges/{str(badge['id'])}/xolo)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["badges"][user_id][str(badge["id"])] = badge
                    database.write(data)
            all_badges = []
            for badge in badges:
                all_badges.append(str(badge["id"]))
            for badge in data["badges"][user_id].copy():
                if badge not in all_badges:
                    embed_data = {"embeds": [{"title": "User Tracker | Badge Removed", "fields": [{"name": "Badge Link", "value": f"[Badge](https://www.roblox.com/badges/{badge}/xolo)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    del data["badges"][user_id][badge]
                    database.write(data)
                        
        except Exception as e:
            print("ERROR: " + str(e))