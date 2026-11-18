import os
import sys
import webbrowser
from pathlib import Path

CONFIG_DIR = Path.home() / ".omnibrowse"
VERIFIED_FILE = CONFIG_DIR / ".social_verified"

BANNER = r"""
  ___                  _ ____                              
 / _ \ _ __ ___  _ __ (_) __ ) _ __ _____      _____  ___ 
| | | | '_ ` _ \| '_ \| |  _ \| '__/ _ \ \ /\ / / __|/ _ \
| |_| | | | | | | | | | | |_) | | | (_) \ V  V /\__ \  __/
 \___/|_| |_| |_|_| |_|_|____/|_|  \___/ \_/\_/ |___/\___|
                                                          
   The Universal Autonomous Browser Engine for AI Agents
============================================================
  Creator & Community Links:
  ⭐ Star on GitHub : https://github.com/aniketkhalko15-blip/omnibrowse
  📸 Instagram      : https://instagram.com/aniket_aegistraton
  ▶️ YouTube        : https://youtube.com/@yamiyugen
============================================================
"""

def print_banner():
    """Display startup banner with creator links."""
    print(BANNER)

def check_social_verification(force_prompt: bool = False):
    """
    Onboarding flow prompting the user to star, subscribe, and follow.
    Opens the links directly for convenience on first run.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if VERIFIED_FILE.exists() and not force_prompt:
        return

    print("\n" + "=" * 62)
    print("  🚀 Welcome to OmniBrowse by Aniket (@aniket_aegistraton)!")
    print("  Before continuing, support the creator & project:")
    print("   1. ⭐ Star Repo : https://github.com/aniketkhalko15-blip/omnibrowse")
    print("   2. 📸 Follow IG : https://instagram.com/aniket_aegistraton")
    print("   3. ▶️ Subscribe  : https://youtube.com/@yamiyugen")
    print("=" * 62)

    try:
        choice = input("\n[?] Open social links in your browser to follow now? (Y/n): ").strip().lower()
        if choice in ["", "y", "yes"]:
            print("[*] Opening links...")
            webbrowser.open("https://github.com/aniketkhalko15-blip/omnibrowse")
            webbrowser.open("https://instagram.com/aniket_aegistraton")
            webbrowser.open("https://www.youtube.com/results?search_query=yami+yugen")
    except Exception:
        pass

    input("\n[✓] Press [Enter] once you've followed and subscribed to launch OmniBrowse! ")
    
    # Save verification flag locally
    try:
        VERIFIED_FILE.write_text("verified=true\n")
    except Exception:
        pass

    print("[*] Thank you for your support! Launching OmniBrowse engine...\n")
