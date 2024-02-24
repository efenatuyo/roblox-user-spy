import asyncio, json
from spy import spyier

asyncio.run(spyier(json.loads(open("config.json", "r").read())).start())