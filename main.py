import time
import requests
import os

# Render environment variables വഴി ടോക്കൺ എടുക്കും
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
ZEE5_API_URL = "https://hons-cb.zee5.com/api/v1/content/tvshow"

SENT_LINKS_FILE = "sent_episodes.txt"

def get_sent_links():
    try:
        with open(SENT_LINKS_FILE, "r") as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

def save_sent_link(link):
    with open(SENT_LINKS_FILE, "a") as f:
        f.write(link + "\n")

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

def check_zee5_updates():
    sent_links = get_sent_links()
    try:
        response = requests.get(ZEE5_API_URL).json()
        show_name = "Kudumbashree Sharada"
        channel_title = "Zee Keralam HD - ZEE5"
        episode_no = "1593"
        episode_title = "Sushmita Plots against Shalini"
        release_time = "2026-09-03 07:04 PM (Thursday) IST"
        watch_link = "https://www.zee5.com/tvshows/details/kudumbashree-sharada/..."

        if watch_link not in sent_links:
            caption = f"""⎔ **New Episode Released**

│ **{show_name}**
├─────────────────
├ **{channel_title}**
├ **Episode {episode_no}**
├ **{episode_title}**
└ **{release_time}**

➤ **Watch Link:**
{watch_link}

│ 🌟─────────────────🌟"""
            send_telegram_message(caption)
            save_sent_link(watch_link)

    except Exception as e:
        print(f"Error checking updates: {e}")

while True:
    check_zee5_updates()
    time.sleep(3600)
  
