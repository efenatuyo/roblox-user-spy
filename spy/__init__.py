import os, random, asyncio

from . import cookie
from . import proxy
from .spyiers import precense_tracker
from .spyiers import friends_tracker
from .spyiers import currently_wearing_tracker
from .spyiers import badges_tracker
from .spyiers import games_created_tracker
from .spyiers import profile_tracker

class spyier:
    precense_users: list = []
    friends_users: list = []
    currently_wearing_users: list = []
    badges_users: list = []
    games_created_users: list = []
    profile_users: list = []
    userPresenceType: list = ['Offline', 'Online', 'In Game', 'In Studio', 'Invisible']
    def __init__(self, config):
        if os.name != 'nt':
            raise OSError("This code is only supported on Windows.")
        
        cookie.check(config["cookie"])
        self.config = config
        self.setup_users()
        self.precense_users = self.split(self.precense_users)
        self.proxies = proxy.make(len(self.precense_users) + len(self.friends_users) + len(self.currently_wearing_users) + len(self.badges_users) + len(self.games_created_users) + len(self.profile_users))
    
    @staticmethod
    def split(input_list: list, max_len: int = 200):
        if len(input_list) <= max_len:
            return [input_list]
        input_list *= -(-max_len // len(input_list))
        return [input_list[i:i+max_len] for i in range(0, len(input_list), max_len)]
        
    def setup_users(self):
        for user, config in self.config["user_ids"].items():
            if config.get("precense_tracker"):
                self.precense_users.append(user)
            if config.get("friends_tracker"):
                self.friends_users.append(user)
            if config.get("currently_wearing_tracker"):
                self.currently_wearing_users.append(user)
            if config.get("badges_tracker"):
                self.badges_users.append(user)
            if config.get("games_created_tracker"):
                self.games_created_users.append(user)
            if config.get("profile_tracker"):
                self.profile_users.append(user)
    
    async def start(self):
        tasks = []
        for user_ids in self.precense_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(precense_tracker.track(self, user_ids, proxy))
        for user_id in self.friends_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(friends_tracker.track(self, user_id, proxy))
        for user_id in self.currently_wearing_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(currently_wearing_tracker.track(self, user_id, proxy))
        for user_id in self.badges_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(badges_tracker.track(self, user_id, proxy))
        for user_id in self.games_created_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(games_created_tracker.track(self, user_id, proxy))
        for user_id in self.profile_users:
            proxy = random.choice(self.proxies)
            self.proxies.remove(proxy)
            tasks.append(profile_tracker.track(self, user_id, proxy))
            
        await asyncio.gather(*tasks)