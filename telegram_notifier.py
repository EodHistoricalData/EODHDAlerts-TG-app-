import aiohttp
import asyncio
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


class TelegramNotifier:
    def __init__(self):
        self.api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    async def send_message(self, message: str):
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, data=payload) as response:
                await response.text()  # Optional: handle or log response
