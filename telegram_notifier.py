# telegram_notifier.py

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    def send_message(self, message: str):
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(self.api_url, data=payload)
