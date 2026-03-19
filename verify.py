import asyncio
from unofficial_livecounts_api import api

async def test_all():
    print("--- TikTok Test ---")
    try:
        users = await api.tiktok.find_user_async("best")
        print(f"Found {len(users)} users on TikTok")
    except Exception as e:
        print(f"TikTok error: {e}")

    print("\n--- YouTube Test ---")
    try:
        channels = await api.youtube.find_channel_async("mrbeast")
        print(f"Found {len(channels)} channels on YouTube")
    except Exception as e:
        print(f"YouTube error: {e}")

    print("\n--- Twitter Test ---")
    try:
        user = await api.twitter.find_user_async("jack")
        print(f"Found Twitter user: {user.display_name}")
    except Exception as e:
        print(f"Twitter error: {e}")

    print("\n--- Twitch Test ---")
    try:
        users = await api.twitch.find_user_async("jack")
        print(f"Found {len(users)} users on Twitch")
    except Exception as e:
        print(f"Twitch error: {e}")

if __name__ == "__main__":
    asyncio.run(test_all())
    
    # Sync example
    print("\n--- Sync Example (TikTok) ---")
    try:
        users_sync = api.tiktok.find_user("best")
        print(f"Found {len(users_sync)} users on TikTok (Sync)")
    except Exception as e:
        print(f"TikTok sync error: {e}")
