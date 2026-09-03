import os
import threading
import time
from bs4 import BeautifulSoup
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

# നിങ്ങൾ നൽകിയ 15 സീരിയലുകളുടെ ലിങ്കുകൾ
TARGET_SHOWS = [
    "https://www.zee5.com/tv-shows/details/aval-arundhati/0-6-4z5757767",
    "https://www.zee5.com/tv-shows/details/snehapoorvam-shyama/0-6-4z5629132",
    "https://www.zee5.com/tv-shows/details/kudumbashree-sharada/0-6-4z5129937",
    "https://www.zee5.com/tv-shows/details/karnan/0-6-4z51012718",
    "https://www.zee5.com/tv-shows/details/mangalyam/0-6-4z5410029",
    "https://www.zee5.com/tv-shows/details/pranayavilasam/0-6-4z5906216",
    "https://www.zee5.com/tv-shows/details/valyettan/0-6-4z5906706",
    "https://www.zee5.com/tv-shows/details/krishnagadha/0-6-4z5782715",
    "https://www.zee5.com/tv-shows/details/durga/0-6-4z5845501",
    "https://www.zee5.com/tv-shows/details/akale/0-6-4z5654322",
    (
        "https://www.zee5.com/tv-shows/details/saregamapa-lil-champs-season-2/0-6-4z51011498"
    ),
    "https://www.zee5.com/tv-shows/details/chembarathy/0-6-4z5825811",
    "https://www.zee5.com/tv-shows/details/meghasandhesham/0-6-4z5782717",
    "https://www.zee5.com/tv-shows/details/ashwathi-nakshatram/0-6-4z5577974",
    "https://www.zee5.com/tv-shows/details/kudumbasametham/0-6-4z5802132",
]

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
    return
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": CHANNEL_ID,
      "text": text,
      "disable_web_page_preview": False,
  }
  requests.post(url, data=payload)


# എല്ലാ സീരിയൽ ലിങ്കുകളും ചെക്ക് ചെയ്യുന്ന ഫങ്ഷൻ
def check_zee5_updates():
  sent_links = get_sent_links()
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  for show_url in TARGET_SHOWS:
    try:
      response = requests.get(show_url, headers=headers)
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        for a in links:
          href = a["href"]
          # പുതിയ എപ്പിസോഡിന്റെ ഡയറക്റ്റ് ലിങ്ക് കണ്ടെത്തുന്നു
          if "/tvshows/details/" in href and href != show_url:
            full_url = (
                href
                if href.startswith("http")
                else f"https://www.zee5.com{href}"
            )

            if full_url not in sent_links:
              show_name = show_url.split("/details/")[1].split("/")[0].replace("-", " ").title()
              caption = f"""⎔ **New Episode Updated**

│ **Show:** {show_name}
├─────────────────
├ **Platform:** ZEE5 Malayalam
└ **Status:** Latest Episode Available

➤ **Watch Link:**
{full_url}

│ 🌟─────────────────🌟"""
              send_telegram_message(caption)
              save_sent_link(full_url)
              time.sleep(1)
    except Exception as e:
      print(f"Error checking show {show_url}: {e}")


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
    time.sleep(300)  # 5 മിനിറ്റ് കൂടുമ്പോൾ എല്ലാ ലിങ്കുകളും ചെക്ക് ചെയ്യും


if __name__ == "__main__":
  t = threading.Thread(target=bot_loop)
  t.start()
  run_web_server()
  
