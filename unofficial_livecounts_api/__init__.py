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

TIKTOK_USER_SEARCH_API = os.getenv("TIKTOK_USER_SEARCH_API", "https://tiktok.livecounts.io/user/search").removesuffix("/")
TIKTOK_USER_STATS_API = os.getenv("TIKTOK_USER_STATS_API", "https://tiktok.livecounts.io/user/stats").removesuffix("/")
TIKTOK_VIDEO_SEARCH_API = os.getenv("TIKTOK_VIDEO_SEARCH_API", "https://tiktok.livecounts.io/video/data").removesuffix("/")
TIKTOK_VIDEO_STATS_API = os.getenv("TIKTOK_VIDEO_STATS_API", "https://tiktok.livecounts.io/video/stats").removesuffix("/")

YOUTUBE_CHANNEL_SEARCH_API = os.getenv("YOUTUBE_CHANNEL_SEARCH_API", "https://api.livecounts.io/youtube-live-subscriber-counter/search").removesuffix("/")
YOUTUBE_VIDEO_SEARCH_API = os.getenv("YOUTUBE_VIDEO_SEARCH_API", "https://api.livecounts.io/youtube-live-view-counter/search").removesuffix("/")
YOUTUBE_CHANNEL_STATS_API = os.getenv("YOUTUBE_CHANNEL_STATS_API", "https://api.livecounts.io/youtube-live-subscriber-counter/stats").removesuffix("/")
YOUTUBE_VIDEO_STATS_API = os.getenv("YOUTUBE_VIDEO_STATS_API", "https://api.livecounts.io/youtube-live-view-counter/stats").removesuffix("/")

TWITTER_USER_SEARCH_API = os.getenv("TWITTER_USER_SEARCH_API", "https://api.livecounts.io/twitter-live-follower-counter/search").removesuffix("/")
TWITTER_USER_STATS_API = os.getenv("TWITTER_USER_STATS_API", "https://api.livecounts.io/twitter-live-follower-counter/stats").removesuffix("/")

TWITCH_USER_SEARCH_API = os.getenv("TWITCH_USER_SEARCH_API", "https://api.livecounts.io/twitch-live-follower-counter/search").removesuffix("/")
TWITCH_USER_STATS_API = os.getenv("TWITCH_USER_STATS_API", "https://api.livecounts.io/twitch-live-follower-counter/stats").removesuffix("/")

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
def __get_default_header(timestamp_ms: int) -> dict[str, str]:
    x_ajay = timestamp_ms
    x_catto = hashlib.new('ripemd160', str(x_ajay).encode()).hexdigest()
    # Using Crypto.Hash if available for RIPEMD160, but fallback to hashlib if needed
    try:
        h = RIPEMD160.new()
        h.update(str(x_ajay).encode("utf-8"))
        x_catto = h.hexdigest()
    except Exception:
        pass
        
    x_midas = hashlib.sha384(hashlib.sha256(str(x_ajay + 64).encode()).hexdigest().encode()).hexdigest()
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "*/*",
        "Origin": "https://livecounts.io",
        "Referer": "https://livecounts.io/",
        "X-Ajay": str(x_ajay),
        "X-Catto": x_catto,
        "X-Midas": x_midas,
    }

def send_request(url: str) -> dict[str, Any]:
    try:
        now_ms = int(datetime.now().timestamp() * 1000)
        response = http_client.get(url=url, headers=__get_default_header(now_ms))
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
        now_ms = int(datetime.now().timestamp() * 1000)
        response = await async_http_client.get(url=url, headers=__get_default_header(now_ms))
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
    async def find_user_async(query: str) -> list[TiktokUser]:
        data = await async_send_request(f"{TIKTOK_USER_SEARCH_API}/{query}")
        return [TiktokUser(i.get("userId", ""), i.get("id", ""), i.get("username", ""), i.get("avatar", ""), i.get("verified", False)) for i in data.get("userData", [])]

    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{TIKTOK_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0), "likes": m.get("likeCount", 0), "following": m.get("followingCount", 0), "videos": m.get("videoCount", 0)}

    @staticmethod
    async def fetch_user_metrics_async(query: str):
        m = await async_send_request(f"{TIKTOK_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0), "likes": m.get("likeCount", 0), "following": m.get("followingCount", 0), "videos": m.get("videoCount", 0)}

class YoutubeAgent:
    @staticmethod
    def find_channel(query: str):
        data = send_request(f"{YOUTUBE_CHANNEL_SEARCH_API}/{query}").get("userData", [])
        return [{"id": i.get("id", ""), "name": i.get("username", ""), "avatar": i.get("avatar", "")} for i in data]

    @staticmethod
    async def find_channel_async(query: str):
        data = await async_send_request(f"{YOUTUBE_CHANNEL_SEARCH_API}/{query}")
        return [{"id": i.get("id", ""), "name": i.get("username", ""), "avatar": i.get("avatar", "")} for i in data.get("userData", [])]

    @staticmethod
    def fetch_channel_metrics(query: str):
        m = send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{query}")
        return {"subscribers": m.get("followerCount", 0), "bottom": m.get("bottomOdos", [0, 0, 0])}

    @staticmethod
    async def fetch_channel_metrics_async(query: str):
        m = await async_send_request(f"{YOUTUBE_CHANNEL_STATS_API}/{query}")
        return {"subscribers": m.get("followerCount", 0), "bottom": m.get("bottomOdos", [0, 0, 0])}

class TwitterAgent:
    @staticmethod
    def find_user(query: str):
        data = send_request(f"{TWITTER_USER_SEARCH_API}/{query}").get("userData", [])
        return {"id": data[0]["id"], "username": data[0]["username"], "avatar": data[0]["avatar"]} if data else None

    @staticmethod
    async def find_user_async(query: str):
        data = await async_send_request(f"{TWITTER_USER_SEARCH_API}/{query}")
        u = data.get("userData", [])
        return {"id": u[0]["id"], "username": u[0]["username"], "avatar": u[0]["avatar"]} if u else None

    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{TWITTER_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0), "bottom": m.get("bottomOdos", [0, 0, 0])}

    @staticmethod
    async def fetch_user_metrics_async(query: str):
        m = await async_send_request(f"{TWITTER_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0), "bottom": m.get("bottomOdos", [0, 0, 0])}

class TwitchAgent:
    @staticmethod
    def find_user(query: str):
        data = send_request(f"{TWITCH_USER_SEARCH_API}/{query}").get("userData", [])
        return [{"id": i.get("id", ""), "username": i.get("username", ""), "avatar": i.get("avatar", "")} for i in data]

    @staticmethod
    async def find_user_async(query: str):
        data = await async_send_request(f"{TWITCH_USER_SEARCH_API}/{query}")
        return [{"id": i.get("id", ""), "username": i.get("username", ""), "avatar": i.get("avatar", "")} for i in data.get("userData", [])]

    @staticmethod
    def fetch_user_metrics(query: str):
        m = send_request(f"{TWITCH_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0)}

    @staticmethod
    async def fetch_user_metrics_async(query: str):
        m = await async_send_request(f"{TWITCH_USER_STATS_API}/{query}")
        return {"followers": m.get("followerCount", 0)}

class LivecountsAPI:
    def __init__(self):
        self.tiktok = TiktokAgent
        self.youtube = YoutubeAgent
        self.twitter = TwitterAgent
        self.twitch = TwitchAgent

api = LivecountsAPI()
