import requests
import time
import os
import random
from urllib.parse import urlparse, parse_qs

# Auto create folders
os.makedirs("logs", exist_ok=True)

def read_file_lines(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except:
        return []

def get_post_id(post_url):
    try:
        if "/posts/" in post_url:
            return post_url.split("/posts/")[1].split("/")[0]
        elif "fbid=" in post_url:
            return parse_qs(urlparse(post_url).query)['fbid'][0]
        elif "/photos/" in post_url:
            return post_url.split("/")[-2]
        else:
            raise ValueError("Unsupported URL format")
    except Exception as e:
        print(f"[ERROR] Extracting post ID: {e}")
        return None

def comment_on_post(token, post_id, message):
    url = f"https://graph.facebook.com/{post_id}/comments"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}
    try:
        r = requests.post(url, headers=headers, data=payload)
        if r.status_code == 200:
            print(f"[SUCCESS] Commented: {message}")
            with open("logs/comment_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{time.ctime()} - {message}\n")
        else:
            print(f"[ERROR] Failed to comment. Status: {r.status_code}, Response: {r.text}")
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

def run_comment_bot():
    tokens = read_file_lines("token.txt")
    post_links = read_file_lines("postlink.txt")
    comments = read_file_lines("comments.txt")
    time_data = read_file_lines("time.txt")
    hater_names = read_file_lines("hatersname.txt")

    if not tokens or not post_links or not comments or not time_data:
        print("Missing one or more required files.")
        return

    try:
        interval = int(time_data[0])  # in seconds
    except:
        print("[ERROR] Invalid time in time.txt")
        return

    post_id = get_post_id(post_links[0])
    if not post_id:
        print("[ERROR] Invalid post link.")
        return

    print("[STARTED] Facebook Auto Comment Bot")

    token_index = 0
    while True:
        token = tokens[token_index % len(tokens)]
        comment = random.choice(comments)

        # If hater list exists, randomly pick a name
        if hater_names:
            hater = random.choice(hater_names)
            comment = comment.replace("{name}", hater)

        comment_on_post(token, post_id, comment)

        token_index += 1
        time.sleep(interval)

if __name__ == "__main__":
    run_comment_bot()
