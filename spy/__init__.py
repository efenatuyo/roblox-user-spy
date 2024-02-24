import os, random, asyncio

from . import cookie
from . import proxy
from . import spyiers
from .spyiers import precense_tracker

class spyier:
    precense_users: list = []
    total_watching_list: int = 0
    userPresenceType: list = ['Offline', 'Online', 'In Game', 'In Studio', 'Invisible']
    def __init__(self, config):
        if os.name != 'nt':
            raise OSError("This code is only supported on Windows.")
        
        cookie.check(config["cookie"])
        self.config = config
        self.setup_users()
        self.precense_users = self.split(self.precense_users)
        self.proxies = proxy.make(len(self.precense_users))
    
    @staticmethod
    def split(input_list: list, max_len: int = 200):
        if len(input_list) <= max_len:
            return [input_list]
        input_list *= -(-max_len // len(input_list))
        return [input_list[i:i+max_len] for i in range(0, len(input_list), max_len)]
        
    def setup_users(self):
        for user, config in self.config["user_ids"].items():
            if config.get("precense_tracker"):
                if not self.precense_users:
                    self.total_watching_list += 1
                self.precense_users.append(user)
    
    async def start(self):
        tasks = []
        for user_ids in self.precense_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(precense_tracker.track(self, user_ids, proxy))
        
        await asyncio.gather(*tasks)