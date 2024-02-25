import aiohttp

from .. import database

async def get_games_created(session, user_id, proxy):
  cursor = None
  games_created = []
  while True:
    async with session.get(f"https://games.roblox.com/v2/users/{user_id}/games?accessFilter=Public&limit=50&cursor={cursor if cursor else ''}", proxy=proxy.current) as response:
        if response.status == 429:
            proxy.next()
            continue
        if response.status == 200:
            json_response = await response.json()
            games_created += json_response["data"]
            if json_response["nextPageCursor"]:
                cursor = json_response["nextPageCursor"]
            else:
                return games_created

async def track(self, user_id, proxy):
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=None), headers={'Accept-Encoding': 'gzip, deflate'})
    while True:
        try:
            games_created = await get_games_created(session, user_id, proxy)
            if games_created is False: continue
            data = database.read()
            if user_id not in data["games_created"]:
                data["games_created"][user_id] = {}
                for game in games_created:
                    data["games_created"][user_id][str(game["rootPlace"]["id"])] = game
                database.write(data)
                continue
            for game in games_created:
                if str(game["rootPlace"]["id"]) not in data["games_created"][user_id]:
                    embed_data = {"embeds": [{"title": "User Tracker | Game Added", "fields": [{"name": "Game Link", "value": f"[Game](https://www.roblox.com/games/{str(game['rootPlace']['id'])})", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["games_created"][user_id][str(game["rootPlace"]["id"])] = game
                    database.write(data)
                differences = {}
                for key, value in data["games_created"][user_id][str(game["rootPlace"]["id"])].items():
                    if key == 'updated' or key == 'placeVisits': continue
                    if key in game and game[key] != value:
                        differences[key] = {'old': value, 'new': game[key], 'key': key}
                for difference in differences:
                    embed_data = {"embeds": [{"title": f"User Tracker | Game Changed {difference}", "fields": [{"name": "Changes", "value": f"from {'**' + differences[difference]['old'] + '**' if differences[difference]['old'] else ''} to {'**' + differences[difference]['new'] + '**' if differences[difference]['new'] else ''}", "inline": False}, {"name": "Game Link", "value": f"[Game](https://www.roblox.com/games/{str(game['rootPlace']['id'])})", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    data["games_created"][user_id][str(game["rootPlace"]["id"])][differences[difference]['key']] = differences[difference]['new']
                    database.write(data)
            all_games_created = []
            for game in games_created:
                all_games_created.append(str(game["rootPlace"]["id"]))
            for game in data["games_created"][user_id].copy():
                if game not in all_games_created:
                    embed_data = {"embeds": [{"title": "User Tracker | Game Removed", "fields": [{"name": "Game Link", "value": f"[Game](https://www.roblox.com/games/{game})", "inline": False}, {"name": "User Profile", "value": f"[Profile](https://www.roblox.com/users/{str(user_id)}/profile)", "inline": False}]}]}
                    await session.post(self.config['webhook'], json=embed_data)
                    del data["games_created"][user_id][game]
                    database.write(data)
                        
        except Exception as e:
            print("ERROR: " + str(e))