import os
import threading
import time
from flask import Flask
import requests

# Web server for Render Free Web Service
app = Flask(__name__)


@app.route("/")
def home():
  return "Zee5 Bot is Running Live!"


def run_web_server():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)


# Telegram Bot Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
ZEE5_API_URL = "https://hons-cb.zee5.com/api/v1/content/tvshow"

SENT_LINKS_FILE = "sent_episodes.txt"
LAST_OFFSET = None


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
  if not BOT_TOKEN or not CHANNEL_ID:
    print("BOT_TOKEN or CHANNEL_ID missing in Environment Variables!")
    return
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": CHANNEL_ID,
      "text": text,
      "disable_web_page_preview": False,
  }
  requests.post(url, data=payload)


def check_zee5_updates():
  sent_links = get_sent_links()
  try:
    # Zee5 Data Checking logic
    show_name = "Kudumbashree Sharada"
    channel_title = "Zee Keralam HD - ZEE5"
    episode_no = "1593"
    episode_title = "Sushmita Plots against Shalini"
    release_time = "2026-09-03 07:04 PM (Thursday) IST"
    watch_link = "https://www.zee5.com/tvshows/details/kudumbashree-sharada/0-6-4z5129937/sushmita-plots-against-shalini/0-1-6z51049298"

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


# /start കമാൻഡിന് മറുപടി നൽകാൻ
def check_start():
  global LAST_OFFSET
  try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {"timeout": 1}
    if LAST_OFFSET:
      params["offset"] = LAST_OFFSET

    res = requests.get(url, params=params).json()
    updates = res.get("result", [])

    for u in updates:
      LAST_OFFSET = u.get("update_id") + 1
      msg = u.get("message", {})
      if msg.get("text") == "/start":
        chat_id = msg.get("chat", {}).get("id")
        reply = "Hi, I am a Zee5 Notification Bot. I am active!"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": reply},
        )
  except Exception as e:
    print(f"Start command error: {e}")


def bot_loop():
  while True:
    check_start()
    check_zee5_updates()
    time.sleep(3)


if __name__ == "__main__":
  # Start Bot in background thread
  t = threading.Thread(target=bot_loop)
  t.start()
  # Start Web Server for Render Port Check
  run_web_server()
  
