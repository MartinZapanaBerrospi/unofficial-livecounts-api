import os
import re
import hashlib
import warnings
import asyncio
from datetime import datetime
from functools import lru_cache
from typing import Any

import httpx
import msgspec
import validators
from Crypto.Hash import RIPEMD160
from latest_user_agents import get_random_user_agent
from dotenv import load_dotenv

# --- Environment Configuration ---
load_dotenv()

PROXY_ENABLED = os.getenv("PROXY_ENABLED", "off")
PROXY_SERVER = os.getenv("PROXY_SERVER", None)

TIKTOK_USER_SEARCH_API = os.getenv("TIKTOK_USER_SEARCH_API", "https://tiktok-api.tokcounter.com/user/search").removesuffix("/")
TIKTOK_USER_STATS_API = os.getenv("TIKTOK_USER_STATS_API", "https://tiktok-api.tokcounter.com/user/stats").removesuffix("/")
TIKTOK_VIDEO_SEARCH_API = os.getenv("TIKTOK_VIDEO_SEARCH_API", "https://tiktok-api.tokcounter.com/video/data").removesuffix("/")
TIKTOK_VIDEO_STATS_API = os.getenv("TIKTOK_VIDEO_STATS_API", "https://tiktok-api.tokcounter.com/video/stats").removesuffix("/")

YOUTUBE_CHANNEL_SEARCH_API = os.getenv("YOUTUBE_CHANNEL_SEARCH_API", "https://api.livecounts.io/youtube-live-subscriber-counter/search").removesuffix("/")
YOUTUBE_VIDEO_SEARCH_API = os.getenv("YOUTUBE_VIDEO_SEARCH_API", "https://api.livecounts.io/youtube-live-view-counter/search").removesuffix("/")
YOUTUBE_CHANNEL_STATS_API = os.getenv("YOUTUBE_CHANNEL_STATS_API", "https://api.livecounts.io/youtube-live-subscriber-counter/stats").removesuffix("/")
YOUTUBE_VIDEO_STATS_API = os.getenv("YOUTUBE_VIDEO_STATS_API", "https://api.livecounts.io/youtube-live-view-counter/stats").removesuffix("/")

TWITTER_USER_SEARCH_API = os.getenv("TWITTER_USER_SEARCH_API", "https://api.livecounts.io/twitter-live-follower-counter/search").removesuffix("/")
TWITTER_USER_STATS_API = os.getenv("TWITTER_USER_STATS_API", "https://api.livecounts.io/twitter-live-follower-counter/stats").removesuffix("/")

TWITCH_USER_SEARCH_API = os.getenv("TWITCH_USER_SEARCH_API", "https://api.livecounts.io/twitch-live-follower-counter/search").removesuffix("/")
TWITCH_USER_STATS_API = os.getenv("TWITCH_USER_STATS_API", "https://api.livecounts.io/twitch-live-follower-counter/stats").removesuffix("/")

KICK_USER_SEARCH_API = os.getenv("KICK_USER_SEARCH_API", "https://api.livecounts.io/kick-live-follower-counter/search").removesuffix("/")
KICK_USER_STATS_API = os.getenv("KICK_USER_STATS_API", "https://api.livecounts.io/kick-live-follower-counter/stats").removesuffix("/")

# --- Errors ---
class RequestApiError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

# --- Utilities & Networking ---
timeout = httpx.Timeout(10.0, connect=5.0)
limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)

def __get_httpx_client():
    proxy = PROXY_SERVER if PROXY_ENABLED == "on" else None
    return httpx.Client(proxy=proxy, timeout=timeout, limits=limits, verify=False)

def __get_httpx_async_client():
    proxy = PROXY_SERVER if PROXY_ENABLED == "on" else None
    return httpx.AsyncClient(proxy=proxy, timeout=timeout, limits=limits, verify=False)

http_client = __get_httpx_client()
async_http_client = __get_httpx_async_client()
warnings.simplefilter("ignore", httpx.NetworkError)

@lru_cache(maxsize=128)
def __get_default_header(timestamp_ms: int, is_tiktok: bool = False) -> dict[str, str]:
    x_ajay = timestamp_ms
    try:
        h = RIPEMD160.new()
        h.update(str(x_ajay).encode("utf-8"))
        x_catto = h.hexdigest()
    except Exception:
        x_catto = hashlib.new('ripemd160', str(x_ajay).encode()).hexdigest()
        
    x_midas = hashlib.sha384(hashlib.sha256(str(x_ajay + 64).encode()).hexdigest().encode()).hexdigest()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://livecounts.io",
        "Referer": "https://livecounts.io/",
        "X-Ajay": str(x_ajay),
        "X-Catto": x_catto,
        "X-Midas": x_midas,
    }
    
    if is_tiktok:
        # TikTok (tokcounter) uses x-catto as timestamp
        headers["X-Catto"] = str(timestamp_ms)
        # x-ajay and x-midas for tokcounter seem to be different hashes
        headers["X-Ajay"] = hashlib.sha1(str(timestamp_ms).encode()).hexdigest()
        headers["X-Midas"] = hashlib.sha256(str(timestamp_ms + 100).encode()).hexdigest()
        
    return headers

def send_request(url: str) -> dict[str, Any]:
    try:
        is_tiktok = "tokcounter.com" in url
        now_ms = int(datetime.now().timestamp() * 1000)
        response = http_client.get(url=url, headers=__get_default_header(now_ms, is_tiktok))
        if response.status_code != 200:
            raise RequestApiError(f"Status: {response.status_code}")
        data = msgspec.json.decode(response.content)
        if not data.get("success", True):
            raise RequestApiError("API Unsuccessful")
        return data
    except Exception as e:
        raise RequestApiError(str(e))

async def async_send_request(url: str) -> dict[str, Any]:
    try:
        is_tiktok = "tokcounter.com" in url
        now_ms = int(datetime.now().timestamp() * 1000)
        response = await async_http_client.get(url=url, headers=__get_default_header(now_ms, is_tiktok))
        if response.status_code != 200:
            raise RequestApiError(f"Status: {response.status_code}")
        data = msgspec.json.decode(response.content)
        if not data.get("success", True):
            raise RequestApiError("API Unsuccessful")
        return data
    except Exception as e:
        raise RequestApiError(str(e))

# --- Data Classes & Agents ---

class TiktokUser:
    def __init__(self, user_id: str, username: str, display_name: str, thumbnail: str, verified: bool = False):
        self.user_id, self.username, self.display_name, self.thumbnail, self.verified = user_id, username, display_name, thumbnail, verified

class TiktokAgent:
    @staticmethod
    def find_user(query: str) -> list[TiktokUser]:
        data = send_request(f"{TIKTOK_USER_SEARCH_API}/{query}")
        return [TiktokUser(i.get("userId", ""), i.get("id", ""), i.get("username", ""), i.get("avatar", ""), i.get("verified", False)) for i in data.get("userData", [])]
    
    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{TIKTOK_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0), "likes": m.get("likeCount", 0), "following": m.get("followingCount", 0), "videos": m.get("videoCount", 0)}

    @staticmethod
    def fetch_video_stats(query: str):
        m = send_request(f"{TIKTOK_VIDEO_STATS_API}/{query}")
        return {"views": m.get("followerCount", 0), "likes": m.get("likeCount", 0), "comments": m.get("videoCount", 0), "shares": m.get("followingCount", 0)}

class YoutubeAgent:
    @staticmethod
    def find_channel(query: str):
        data = send_request(f"{YOUTUBE_CHANNEL_SEARCH_API}/{query}")
        return data.get("list", [])
    
    @staticmethod
    def find_video(query: str):
        data = send_request(f"{YOUTUBE_VIDEO_SEARCH_API}/{query}")
        return data.get("list", [])

class TwitterAgent:
    @staticmethod
    def find_user(query: str):
        data = send_request(f"{TWITTER_USER_SEARCH_API}/{query}")
        return data.get("list", [{}])[0] if data.get("list") else None
    
    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{TWITTER_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0)}

class TwitchAgent:
    @staticmethod
    def find_user(query: str):
        data = send_request(f"{TWITCH_USER_SEARCH_API}/{query}")
        return data.get("list", [])
    
    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{TWITCH_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0)}

class KickAgent:
    @staticmethod
    def find_user(query: str):
        data = send_request(f"{KICK_USER_SEARCH_API}/{query}")
        return data.get("list", [])
    
    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{KICK_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0)}

class LivecountsAPI:
    def __init__(self):
        self.tiktok = TiktokAgent()
        self.youtube = YoutubeAgent()
        self.twitter = TwitterAgent()
        self.twitch = TwitchAgent()
        self.kick = KickAgent()

api = LivecountsAPI()
