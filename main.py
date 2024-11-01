import requests
import random
import string
import time
import traceback

# 設定
TOKEN_FILE = "tokens.txt"
LOG_FILE = "script.log"
MESSAGES_PER_TOKEN = 50  # 50メッセージごとにトークンを変更
MESSAGE_LENGTH = 100  # メッセージの長さ

def load_tokens(token_file):
    try:
        with open(token_file, "r") as file:
            tokens = file.read().splitlines()
        log(f"[INFO] Loaded {len(tokens)} tokens.")
        return tokens
    except FileNotFoundError:
        log(f"[ERROR] Token file '{token_file}' not found.")
        return []

def generate_random_message(length=MESSAGE_LENGTH):
    characters = string.ascii_letters + string.digits
    random_message = ''.join(random.choices(characters, k=length))
    log(f"[DEBUG] Generated random message: {random_message}")
    return random_message

def send_message_to_discord(channel_id, token, message):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    json_body = {"content": message, "tts": False}
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"

    try:
        response = requests.post(url, headers=headers, json=json_body, timeout=5)
        
        if response.status_code == 200:
            log(f"[INFO] Successfully sent message: {message}")
        else:
            log(f"[ERROR] Failed to send message, status code: {response.status_code}, response: {response.text}")
    except requests.exceptions.RequestException as e:
        log(f"[ERROR] Exception occurred: {e}")
        log(traceback.format_exc())  # エラースタックをログに出力

def log(message):
    try:
        with open(LOG_FILE, "a") as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception as e:
        print(f"[CRITICAL] Logging error: {e}")

def main():
    channel_id = input("Enter the channel ID: ")
    delay_ms = int(input("Enter delay between messages (milliseconds): "))

    tokens = load_tokens(TOKEN_FILE)
    if not tokens:
        log("[CRITICAL] No tokens found. Please ensure the token file is correctly configured.")
        return

    message_count = 0
    log("[INFO] Starting to send random messages to Discord...")

    while True:
        # 50メッセージごとにトークンを変更
        if message_count % MESSAGES_PER_TOKEN == 0:
            token = random.choice(tokens)
            log(f"[DEBUG] Selected new token.")

        # ランダムなメッセージを生成
        message = generate_random_message()
        # メッセージをディスコードに送信
        try:
            send_message_to_discord(channel_id, token, message)
        except Exception as e:
            log(f"[ERROR] Unexpected error in send_message_to_discord: {e}")
            log(traceback.format_exc())  # エラースタックをログに出力

        # メッセージカウントを増加
        message_count += 1
        # 次のメッセージ送信まで待機 (ミリ秒を秒に変換)
        time.sleep(delay_ms / 1000.0)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            log(f"[CRITICAL] Unexpected error in main loop: {e}")
            log(traceback.format_exc())
            time.sleep(5)  # 一定時間待機してリトライ
