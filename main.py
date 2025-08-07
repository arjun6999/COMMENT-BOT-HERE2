import requests
import time
import os
from urllib.parse import urlparse
import re

# Helper: Extract Post ID from Facebook URL
def extract_post_id(url):
    try:
        if "posts/" in url:
            return url.split("posts/")[1].split("/")[0]
        match = re.search(r"fbid=(\d+)", url)
        if match:
            return match.group(1)
    except Exception as e:
        print("Error extracting post ID:", e)
    return None

# Helper: Log message
def log(msg):
    print(msg)
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Load files
try:
    with open("token.txt", "r") as f:
        token = f.read().strip()
    with open("comments.txt", "r", encoding="utf-8") as f:
        comments = [c.strip() for c in f.readlines() if c.strip()]
    with open("postlink.txt", "r") as f:
        post_url = f.read().strip()
    with open("time.txt", "r") as f:
        delay = int(f.read().strip()) / 1000
    with open("hatersname.txt", "r", encoding="utf-8") as f:
        hater = f.read().strip()
except Exception as e:
    log(f"[ERROR] Failed to load files: {e}")
    exit()

# Extract post ID
post_id = extract_post_id(post_url)
if not post_id:
    log("[ERROR] Invalid post URL or can't extract post ID.")
    exit()

# Comment loop
index = 0
while True:
    comment = comments[index % len(comments)]
    final_comment = comment.replace("{name}", hater)

    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {
        "message": final_comment,
        "access_token": token
    }

    try:
        response = requests.post(url, data=payload)
        data = response.json()

        if "id" in data:
            log(f"[✅] Commented: {final_comment}")
        else:
            log(f"[❌] Failed: {data}")
            if "error" in data:
                err_msg = data["error"].get("message", "")
                if "temporarily blocked" in err_msg.lower():
                    log("[⚠️] Blocked temporarily. Sleeping for 10 minutes.")
                    time.sleep(600)
                    continue
        index += 1
        time.sleep(delay)

    except Exception as e:
        log(f"[💥] Exception occurred: {e}")
        time.sleep(delay)
