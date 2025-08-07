import requests
import time
import random
import os
import re

def extract_post_id(post_url):
    try:
        # For normal /posts/ID format
        match = re.search(r'/posts/(\d+)', post_url)
        if match:
            return match.group(1)

        # Try pfbid decoding (fallback)
        match = re.search(r'/posts/(pfbid[0-9A-Za-z]+)', post_url)
        if match:
            pfbid = match.group(1)
            # Fake fallback logic: simulate a working ID (mocked)
            print(f"[!] Using fallback for pfbid: {pfbid}")
            return post_url.split("fbid=")[-1].split("&")[0] if "fbid=" in post_url else None
    except:
        pass
    return None

def load_file_lines(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return []

def main():
    post_links = load_file_lines("postlink.txt")
    comments = load_file_lines("comments.txt")
    tokens = load_file_lines("token.txt")
    interval_lines = load_file_lines("time.txt")
    haters = load_file_lines("hatersname.txt")

    if not post_links or not comments or not tokens:
        print("Missing required files or contents!")
        return

    try:
        interval = int(interval_lines[0]) if interval_lines else 5
    except:
        interval = 5

    while True:
        token = random.choice(tokens)
        post_url = random.choice(post_links)
        comment_text = random.choice(comments)
        hater = random.choice(haters) if haters else "🤡"

        post_id = extract_post_id(post_url)
        if not post_id:
            print(f"[❌] Invalid post URL or can't extract post ID: {post_url}")
            time.sleep(2)
            continue

        url = f"https://graph.facebook.com/v19.0/{post_id}/comments"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"message": f"{comment_text} {hater}"}

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            print(f"[✅] Commented on {post_id}: {data['message']}")
        else:
            print(f"[⚠️] Failed on {post_id}: {response.text}")

        time.sleep(interval)

if __name__ == "__main__":
    main()
