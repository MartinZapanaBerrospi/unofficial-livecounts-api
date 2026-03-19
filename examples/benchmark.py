import asyncio
import time
from unofficial_livecounts_api.tiktok import TiktokAgent
from unofficial_livecounts_api.youtube import YoutubeAgent

def sync_benchmark():
    print("Running synchronous benchmark...")
    start = time.perf_counter()
    
    # Simulate some typical usage
    users = ["mrbeast", "pewdiepie", "tseries"]
    for user in users:
        try:
            # We use youtube as an example as it's often more stable for search
            YoutubeAgent.find_channel(user)
        except Exception:
            pass
            
    end = time.perf_counter()
    print(f"Sync benchmark finished in {end - start:.2f} seconds")
    return end - start

async def async_benchmark():
    print("Running asynchronous benchmark...")
    start = time.perf_counter()
    
    users = ["mrbeast", "pewdiepie", "tseries"]
    tasks = [YoutubeAgent.find_channel_async(user) for user in users]
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    end = time.perf_counter()
    print(f"Async benchmark finished in {end - start:.2f} seconds")
    return end - start

if __name__ == "__main__":
    # Note: This requires an internet connection and might be affected by rate limiting
    # It's intended to show the potential speedup from concurrency
    sync_time = sync_benchmark()
    async_time = asyncio.run(async_benchmark())
    
    if async_time > 0:
        speedup = sync_time / async_time
        print(f"\nSpeedup: {speedup:.2f}x")
    else:
        print("\nAsync time was 0, cannot calculate speedup.")
