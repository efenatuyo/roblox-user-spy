import aiohttp

from .. import database

async def get_profile(session, user_id, proxy):
    async with session.get(f"https://users.roblox.com/v1/users/{user_id}", proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            return False
        if response.status == 200:
            return await response.json()
    
async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            profile = await get_profile(session, user_id, proxy)
            if not profile: continue
            data = database.read()
            if user_id not in data["profile"]:
                data["profile"][user_id] = profile
                database.write(data)
                continue
            differences = {}
            for key, value in data["profile"][user_id].items():
                if key in profile and profile[key] != value:
                    differences[key] = {'old': value, 'new': profile[key]}
            for difference in differences:
                embed_data = {"embeds": [{"title": f"User Tracker | Profile Changed {difference}", "fields": [{"name": "Changes", "value": f"from {'**' + differences[difference]['old'] + '**' if differences[difference]['old'] else ''} to {'**' + differences[difference]['new'] + '**' if differences[difference]['new'] else ''}", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                await session.post(self.config['webhook'], json=embed_data)
                data["profile"][user_id][difference] = differences[difference]["new"]
                database.write(data)
        except Exception as e:
            print("ERROR: " + str(e))