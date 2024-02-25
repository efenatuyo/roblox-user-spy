import aiohttp

from .. import database

async def get_friends(session, user_id, proxy):
    async with session.get(f"https://friends.roblox.com/v1/users/{user_id}/friends", proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            return False
        if response.status == 200:
            return (await response.json())["data"]

async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            friends = await get_friends(session, user_id, proxy)
            if friends is False: continue
            data = database.read()
            if user_id not in data["friends"]:
                data["friends"][user_id] = {}
                for friend in friends:
                    data["friends"][user_id][str(friend["id"])] = friend
                database.write(data)
                continue
            for friend in friends:
                if str(friend["id"]) not in data["friends"][user_id]:
                    embed_data = {"embeds": [{"title": "User Tracker | Friend Added", "fields": [{"name": "Friend User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(friend['id'])}/profile)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["friends"][user_id][str(friend["id"])] = friend
                    database.write(data)
            all_friends = []
            for friend in friends:
                all_friends.append(str(friend['id']))
            for friend in data["friends"][user_id].copy():
                if friend not in all_friends:
                    embed_data = {"embeds": [{"title": "User Tracker | Friend Removed", "fields": [{"name": "Friend User Profile", "value": f"[Profile](https://www.roblox.com/users/{friend}/profile)", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    del data["friends"][user_id][friend]
                    database.write(data)
                        
        except Exception as e:
            print("ERROR: " + str(e))