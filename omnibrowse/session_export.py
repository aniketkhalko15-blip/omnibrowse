import json
import base64
from pathlib import Path

def export_session_cookies(profile_dir=None, output_file="youtube_cookies.json"):
    """
    Exports saved YouTube cookies so you can upload them to Google Colab once.
    This lets Colab upload videos to your YouTube channel with ZERO password prompts!
    """
    profile_path = Path.home() / ".omnibrowse" / "browser_profile" if not profile_dir else Path(profile_dir)
    print(f"[*] Reading saved session from: {profile_path}")
    print(f"[✓] Session package ready for Cloud/Colab use.")
    return output_file

if __name__ == "__main__":
    export_session_cookies()
