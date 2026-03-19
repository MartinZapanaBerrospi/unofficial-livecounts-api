from unofficial_livecounts_api.tiktok import TiktokAgent
from unofficial_livecounts_api.youtube import YoutubeAgent
from unofficial_livecounts_api.twitter import TwitterAgent
from unofficial_livecounts_api.twitch import TwitchAgent

class LivecountsAPI:
    def __init__(self):
        self.tiktok = TiktokAgent
        self.youtube = YoutubeAgent
        self.twitter = TwitterAgent
        self.twitch = TwitchAgent

api = LivecountsAPI()
