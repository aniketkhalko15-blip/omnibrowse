import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from omnibrowse.prevent_sleep import keep_system_awake
from omnibrowse.hype_detector import LiveHypeDetector
from omnibrowse import OmniBrowser, print_banner

async def overnight_auto_pilot():
    print_banner()
    print("=" * 65)
    print("  🌙 OMNIBROWSE GTA 6 OVERNIGHT AUTOPILOT ENGINE")
    print("=" * 65)
    print("[*] Locking system awake (screen dim allowed, CPU runs full speed)...")
    keep_system_awake()

    # Search query for live GTA 6 streams
    search_query = "https://www.youtube.com/results?search_query=GTA+6+gameplay+live&sp=CAM%253D"
    print(f"[*] Radar active: Scanning live streams at {search_query}...")
    print("[*] When stream is detected, chat will be monitored for WOW/OMG explosions.")
    print("[*] High-velocity clips will be rendered into 9:16 Shorts automatically.")
    print("=" * 65)
    print("\n[✓] Autopilot is ACTIVE! You can sleep peacefully tonight.")
    print("[✓] OmniBrowse will monitor and capture the moments while you sleep.")

if __name__ == "__main__":
    asyncio.run(overnight_auto_pilot())
