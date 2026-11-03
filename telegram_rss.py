import os
import json
import requests
import feedparser
import html
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
RSS_URL = "https://farad017.github.io/Naijanews/feed.xml"
STATE_FILE = "posted_links.json"

# Maximum messages to send per run to avoid Telegram anti-spam blocks
MAX_MESSAGES_PER_RUN = 10 

def load_posted_links():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_posted_links(links):
    with open(STATE_FILE, 'w') as f:
        json.dump(list(links), f)

def send_telegram_message(title, link):
    safe_title = html.escape(title)
    text = f"📰 <a href='{link}'>{safe_title}</a>"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        # Handle Telegram Rate Limiting (Error 429)
        if response.status_code == 429:
            retry_after = response.json().get("parameters", {}).get("retry_after", 30)
            print(f"Rate limited by Telegram. Sleeping for {retry_after} seconds...")
            time.sleep(retry_after)
            return send_telegram_message(title, link) # Retry the message
            
        response.raise_for_status()
        print(f"Transmission successful: {title[:50]}...")
        return True
        
    except Exception as e:
        print(f"Transmission failed for '{title}': {e}")
        return False

def main():
    posted = load_posted_links()
    feed = feedparser.parse(RSS_URL)
    new_count = 0

    # Process from oldest to newest
    for entry in reversed(feed.entries):
        link = entry.link
        if link not in posted:
            success = send_telegram_message(entry.title, link)
            if success:
                posted.add(link)
                new_count += 1
                time.sleep(2) # 2 second delay between messages
                
                # Stop after 10 messages to avoid hitting rate limits
                if new_count >= MAX_MESSAGES_PER_RUN:
                    print(f"Reached max limit of {MAX_MESSAGES_PER_RUN} messages for this run.")
                    break
            else:
                print("Failed to send message. Breaking out of loop.")
                break 

    save_posted_links(posted)
    
    if new_count > 0:
        print(f"Synchronization complete. Transmitted {new_count} new na1ra1and nodes.")
    else:
        print("No new na1ra1and nodes detected. System idle.")

if __name__ == "__main__":
    main()
