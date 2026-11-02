import os
import json
import requests
import feedparser
import html

# =====================================================================
# na1ra1and Autonomous Broadcast Protocol v1.1
# Classified: Eyes Only
# =====================================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
RSS_URL = "https://farad017.github.io/Naijanews/feed.xml"
STATE_FILE = "posted_links.json"

def load_posted_links():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_posted_links(links):
    with open(STATE_FILE, 'w') as f:
        json.dump(list(links), f)

def send_telegram_message(title, link):
    # Escape HTML characters in the title to prevent formatting errors
    safe_title = html.escape(title)
    
    # The new single-line HTML format
    text = f"📰 <a href='{link}'>{safe_title}</a>"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML", # Changed to HTML for robust link handling
        "disable_web_page_preview": False # Changed to False so the article preview shows up
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Transmission successful: {title[:50]}...")
    except Exception as e:
        print(f"Transmission failed for '{title}': {e}")

def main():
    print("Initiating na1ra1and synchronization...")
    posted = load_posted_links()
    feed = feedparser.parse(RSS_URL)
    new_count = 0

    for entry in reversed(feed.entries):
        link = entry.link
        if link not in posted:
            send_telegram_message(entry.title, link)
            posted.add(link)
            new_count += 1

    if new_count > 0:
        save_posted_links(posted)
        print(f"Synchronization complete. Transmitted {new_count} new na1ra1and nodes.")
    else:
        print("No new na1ra1and nodes detected. System idle.")

if __name__ == "__main__":
    main()