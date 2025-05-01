# bot.py

from telegram.ext import Updater, CommandHandler
from config import TELEGRAM_BOT_TOKEN
from handlers import start, set_symbol, set_interval, get_price, analyse_market
from telegram.ext import JobQueue


def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("set_symbol", set_symbol))
    dp.add_handler(CommandHandler("set_interval", set_interval))
    dp.add_handler(CommandHandler("get_price", get_price))

    job_queue: JobQueue = updater.job_queue
    job_queue.run_repeating(analyse_market, interval=60, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
