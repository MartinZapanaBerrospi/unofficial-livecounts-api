import os
import hashlib
import warnings
from datetime import datetime
from functools import lru_cache
from typing import Any
from urllib.parse import quote

import httpx
import msgspec
from latest_user_agents import get_random_user_agent
from dotenv import load_dotenv

# --- Environment Configuration ---
load_dotenv()
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "off")
PROXY_SERVER = os.getenv("PROXY_SERVER", None)

TIKTOK_USER_SEARCH_API = os.getenv("TIKTOK_USER_SEARCH_API", "https://tiktok-api.tokcounter.com/user/search").removesuffix("/")
TIKTOK_USER_STATS_API = os.getenv("TIKTOK_USER_STATS_API", "https://tiktok-api.tokcounter.com/user/stats").removesuffix("/")
TIKTOK_VIDEO_STATS_API = os.getenv("TIKTOK_VIDEO_STATS_API", "https://tiktok-api.tokcounter.com/video/stats").removesuffix("/")

YOUTUBE_CHANNEL_SEARCH_API = os.getenv("YOUTUBE_CHANNEL_SEARCH_API", "https://api.livecounts.io/youtube-live-subscriber-counter/search").removesuffix("/")
YOUTUBE_VIDEO_SEARCH_API = os.getenv("YOUTUBE_VIDEO_SEARCH_API", "https://api.livecounts.io/youtube-live-view-counter/search").removesuffix("/")
YOUTUBE_CHANNEL_STATS_API = os.getenv("YOUTUBE_CHANNEL_STATS_API", "https://api.livecounts.io/youtube-live-subscriber-counter/stats").removesuffix("/")
YOUTUBE_VIDEO_STATS_API = os.getenv("YOUTUBE_VIDEO_STATS_API", "https://api.livecounts.io/youtube-live-view-counter/stats").removesuffix("/")

class RequestApiError(Exception): pass

# --- Networking ---
http_client = httpx.Client(proxy=PROXY_SERVER if PROXY_ENABLED == "on" else None, timeout=12.0, verify=False)
warnings.simplefilter("ignore", httpx.NetworkError)

@lru_cache(maxsize=128)
def __get_default_header(timestamp_ms: int) -> dict[str, str]:
    ts = str(timestamp_ms)
    return {
        "User-Agent": get_random_user_agent(),
        "Origin": "https://livecounts.io",
        "Referer": "https://livecounts.io/",
        "X-Ajay": hashlib.sha1(ts.encode()).hexdigest(),
        "X-Catto": ts,
        "X-Midas": hashlib.sha384(hashlib.sha256(ts.encode()).hexdigest().encode()).hexdigest(),
    }

def send_request(url: str) -> dict[str, Any]:
    try:
        now_ms = int(datetime.now().timestamp() * 1000)
        response = http_client.get(url, headers=__get_default_header(now_ms))
        if response.status_code != 200: raise RequestApiError(f"HTTP {response.status_code}")
        data = msgspec.json.decode(response.content)
        if not data.get("success", True): raise RequestApiError("API Failed")
        return data
    except Exception as e: raise RequestApiError(str(e))

# --- Agents ---
class TiktokAgent:
    def find_user(self, q: str):
        data = send_request(f"{TIKTOK_USER_SEARCH_API}/{quote(q)}")
        return [{"userId": i.get("userId"), "id": i.get("id"), "username": i.get("username"), "avatar": i.get("avatar")} for i in data.get("userData", [])]
    def fetch_user_metrics(self, q: str):
        m = send_request(f"{TIKTOK_USER_STATS_API}/{quote(q)}")
        return {"followers": m.get("followerCount", 0), "likes": m.get("likeCount", 0), "following": m.get("followingCount", 0), "videos": m.get("videoCount", 0)}

class YoutubeAgent:
    def find_channel(self, q: str):
        data = send_request(f"{YOUTUBE_CHANNEL_SEARCH_API}/{quote(q)}")
        return data.get("list", data.get("userData", []))
    def find_video(self, q: str):
        data = send_request(f"{YOUTUBE_VIDEO_SEARCH_API}/{quote(q)}")
        return data.get("list", data.get("userData", []))

class LivecountsAPI:
    def __init__(self):
        self.tiktok, self.youtube = TiktokAgent(), YoutubeAgent()

api = LivecountsAPI()
