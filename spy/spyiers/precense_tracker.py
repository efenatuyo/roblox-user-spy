import aiohttp

from .. import database

async def get_precense(session, user_ids, proxy):
    async with session.post("https://presence.roblox.com/v1/presence/users", json={"userIds": user_ids}, proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            return False
        if response.status == 200:
            return (await response.json())["userPresences"]
    
async def track(self, user_ids, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            response = await get_precense(session, user_ids, proxy)
            if not response: continue
            for user in response:
                data = database.read()
                if str(user["userId"]) not in data["precense"]:
                    data["precense"][str(user["userId"])] = {"online_status": str(user["userPresenceType"])}
                    database.write(data)
                    continue
                if str(user["userPresenceType"]) != data["precense"][str(user["userId"])]["online_status"]:
                    embed_data = {"embeds": [{"title": "User Tracker | Precense", "fields": [{"name": "Online Status", "value": f"from **{str(self.userPresenceType[int(data['precense'][str(user['userId'])]['online_status'])])}** to **{str(self.userPresenceType[int(user['userPresenceType'])])}**", "inline": False},{"name": "Last Location", "value": str(user.get('lastLocation')),"inline": False},{"name": "Place ID","value": str(user.get('placeId')),"inline": False},{"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user['userId'])}/profile)", "inline": False},{"name": "Last Online", "value": str(user['lastOnline']),"inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["precense"][str(user["userId"])] = {"online_status": str(user["userPresenceType"])}
                    database.write(data)
        except Exception as e:
            print("ERROR: " + str(e))