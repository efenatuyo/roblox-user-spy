import aiohttp

from .. import database

async def get_groups(session, user_id, proxy):
    async with session.get(f"https://groups.roblox.com/v2/users/{user_id}/groups/roles", proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            return False
        if response.status == 200:
            return (await response.json())["data"]

async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            groups = await get_groups(session, user_id, proxy)
            if groups is False: continue
            data = database.read()
            if user_id not in data["groups"]:
                data["groups"][user_id] = {}
                for group in groups:
                    data["groups"][user_id][group["group"]["id"]] = group
                database.write(data)
                continue
            for group in groups:
                if str(group["group"]["id"]) not in data["groups"][user_id]:
                    embed_data = {"embeds": [{"title": "User Tracker | Group Added", "fields": [{"name": "Group Link", "value": f"[Group](https://www.roblox.com/groups/{str(group['group']['id'])}/xolo)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["groups"][user_id][str(group["group"]["id"])] = group
                    database.write(data)
            all_groupds = []
            for group in groups:
                all_groupds.append(str(group["group"]["id"]))
            for group in data["groups"][user_id].copy():
                if group not in all_groupds:
                    embed_data = {"embeds": [{"title": "User Tracker | Group Left", "fields": [{"name": "Badge Link", "value": f"[Group](https://www.roblox.com/groups/{group}/xolo)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    del data["badges"][user_id][group]
                    database.write(data)
                        
        except Exception as e:
            print("ERROR: " + str(e))