import asyncio
import time
from typing import Dict, Any, List
from omnibrowse import OmniBrowser, print_banner

# Trigger words that indicate peak hype or crazy moments
HYPE_KEYWORDS = [
    "omg", "wow", "wtf", "no way", "holy", "insane", "pog", "lmao", 
    "crazy", "look at that", "did you see", "sheeeesh", "rip", "bug", "glitch"
]

class LiveHypeDetector:
    """
    Monitors live YouTube stream chat in real-time.
    When chat velocity explodes with hype keywords (WOW, OMG, INSANE),
    it flags the timestamp as a peak viral moment to clip!
    """

    def __init__(self, stream_url: str):
        self.stream_url = stream_url
        self.browser = None
        self.hype_spikes = []

    async def start_monitoring(self, duration_seconds: int = 120):
        print_banner()
        print(f"[*] OmniBrowse Hype Radar: Attaching to stream {self.stream_url}")
        print(f"[*] Monitoring live chat velocity for {duration_seconds} seconds...")

        self.browser = OmniBrowser(headless=False)
        await self.browser.start()

        try:
            await self.browser.goto(self.stream_url)
            await asyncio.sleep(5)

            # Look for YouTube live chat frame / container
            print("[*] Hooking into live chat feed...")

            start_time = time.time()
            last_checked_msg_count = 0

            while time.time() - start_time < duration_seconds:
                # Extract recent chat messages from DOM
                chat_stats = await self.browser.page.evaluate('''() => {
                    const messages = Array.from(document.querySelectorAll('yt-live-chat-text-message-renderer #message')).map(m => m.innerText.toLowerCase());
                    return {
                        total: messages.length,
                        recent: messages.slice(-25)
                    };
                }''')

                recent_msgs = chat_stats.get("recent", [])
                total_msgs = chat_stats.get("total", 0)

                # Count hype keywords
                hype_count = 0
                for msg in recent_msgs:
                    if any(k in msg for k in ["wow", "omg", "wtf", "crazy", "insane", "no way", "lmao"]):
                        hype_count += 1

                current_timestamp = int(time.time() - start_time)

                # If more than 40% of recent messages are screaming WOW / OMG -> SPIKE DETECTED!
                if len(recent_msgs) >= 5 and (hype_count / len(recent_msgs)) >= 0.4:
                    print(f"\n🚨 [HYPE SPIKE DETECTED at +{current_timestamp}s!]")
                    print(f"   Chat Velocity: {hype_count}/{len(recent_msgs)} messages hype!")
                    print(f"   Sample reactions: {recent_msgs[-3:]}")
                    self.hype_spikes.append({
                        "timestamp_offset": current_timestamp,
                        "hype_ratio": hype_count / len(recent_msgs),
                        "sample": recent_msgs[-3:]
                    })

                await asyncio.sleep(2)

            print("\n" + "=" * 60)
            print(f"  🏁 MONITORING COMPLETE: Found {len(self.hype_spikes)} Viral Moments!")
            print("=" * 60)

        finally:
            await self.browser.close()

if __name__ == "__main__":
    detector = LiveHypeDetector("https://www.youtube.com/live")
    print("[✓] LiveHypeDetector initialized and ready.")
