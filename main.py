import requests
import time
import random
import re
import os
from urllib.parse import urlparse, parse_qs

def extract_post_id(url):
    # Handle ?app=fbl links and redirection
    if "facebook.com" not in url:
        return None

    # Try to extract from pfbid or story_fbid or normal ID
    patterns = [
        r"/posts/(\d+)",  # normal posts
        r"story_fbid=(\d+)",  # story links
        r"fbid=(\d+)",  # fbid
        r"/videos/(\d+)",  # videos
        r"/photo.php\?fbid=(\d+)",  # photos
        r"/(\d+)/\?app",  # mobile app links
        r"/permalink/(\d+)",  # permalink
        r"/(\d+)\?type",  # type param
        r"pfbid[A-Za-z0-9]+",  # pfbid
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            group = match.group()
            # Handle pfbid case
            if "pfbid" in group:
                # Optional: convert pfbid to numeric post ID (needs Graph API call)
                response = requests.get(url)
                match2 = re.search(r'"top_level_post_id":"(\d+)"', response.text)
                if match2:
                    return match2.group(1)
            else:
                return match.group(1)
    return None

def load_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        print(f"⚠️ File not found or unreadable: {filename}")
        return []

# Load all required data
tokens = load_file("token.txt")
comments = load_file("comments.txt")
haters = load_file("hatersname.txt")
time_gap = int(load_file("time.txt")[0])
post_link = load_file("postlink.txt")[0]

post_id = extract_post_id(post_link)
if not post_id:
    print("❌ Invalid post URL or can't extract post ID.")
    exit()

print(f"✅ Targeting Post ID: {post_id}")
print("🚀 Starting Comment Bot...\n")

while True:
    for token in tokens:
        try:
            comment = random.choice(comments)
            hater = random.choice(haters)
            full_comment = f"{hater} {comment}"

            url = f"https://graph.facebook.com/{post_id}/comments"
            payload = {
                "message": full_comment,
                "access_token": token
            }
            r = requests.post(url, data=payload)
            data = r.json()

            if "id" in data:
                print(f"✅ Commented: {full_comment}")
            else:
                print(f"❌ Error: {data}")

        except Exception as e:
            print(f"⚠️ Exception: {e}")
        time.sleep(time_gap / 1000)  # Convert ms to sec
