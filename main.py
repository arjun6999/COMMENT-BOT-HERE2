import requests
import time
import os
import random
import re
from urllib.parse import urlparse, parse_qs
from flask import Flask

# Flask app to keep bot alive
app = Flask(__name__)

@app.route("/")
def home():
    return "🔥 Facebook Auto Comment Bot is Running 🔥"

# Load files
def read_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_post_id_from_url(url):
    try:
        if "/posts/" in url:
            return url.split("/posts/")[1].split("/")[0]
        elif "/permalink/" in url:
            return url.split("/permalink/")[1].split("/")[0]
        elif "/photos/" in url:
            return re.search(r"a\.\d+/\d+", url).group().split("/")[1]
        elif "fbid=" in url:
            return parse_qs(urlparse(url).query)["fbid"][0]
        else:
            html = requests.get(url).text
            match = re.search(r'content="https://www.facebook.com/.*/posts/(\d+)"', html)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"[❌] Error extracting post ID: {e}")
    return None

# Load config
tokens = read_file("token.txt")
comments = read_file("comments.txt")
haters = read_file("hatersname.txt")
interval = int(read_file("time.txt")[0])  # seconds
post_urls = read_file("postlink.txt")

# Extract post IDs
post_ids = []
for url in post_urls:
    post_id = get_post_id_from_url(url)
    if post_id:
        post_ids.append(post_id)
    else:
        print(f"[⚠️] Failed to extract post ID from: {url}")

if not post_ids:
    print("[❌] No valid post IDs found. Exiting.")
    exit()

def comment_on_post(token, post_id, message):
    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {
        "message": message,
        "access_token": token
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print(f"[✅] Commented on post {post_id} | Message: {message}")
        else:
            print(f"[❌] Failed on post {post_id} | Error: {r.text}")
    except Exception as e:
        print(f"[⚠️] Exception on post {post_id}: {e}")

print("🔥 Auto Comment Bot Started 🔥")
print(f"[⏱️] Interval set to {interval} seconds\n")

# Background loop
def run_bot():
    while True:
        for token in tokens:
            for post_id in post_ids:
                comment = f"{random.choice(haters)} {random.choice(comments)}"
                comment_on_post(token, post_id, comment)
                print(f"[🕒] Waiting {interval} seconds before next comment...\n")
                time.sleep(interval)

# Start bot in background
import threading
threading.Thread(target=run_bot).start()

# Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
