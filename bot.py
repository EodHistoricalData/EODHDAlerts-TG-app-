# bot.py

import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, JobQueue
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start,
    set_symbol,
    set_interval,
    get_price,
    list_strategies,
    set_strategy,
    strategy_button,
    current_strategy,
    analyse_market,
)


# Set up root logger so you can see INFO/debug from handlers
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def main() -> None:
    """Bootstrap the Telegram bot, register command handlers and schedule market analysis."""
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher
    jq: JobQueue = updater.job_queue

    # Register all command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("set_symbol", set_symbol))
    dp.add_handler(CommandHandler("set_interval", set_interval))
    dp.add_handler(CommandHandler("get_price", get_price))
    dp.add_handler(CommandHandler("list_strategies", list_strategies))
    dp.add_handler(CommandHandler("set_strategy", set_strategy))
    dp.add_handler(CommandHandler("current_strategy", current_strategy))

    dp.add_handler(
        CallbackQueryHandler(strategy_button, pattern=r"^setstrat:")
    )

    start_msg = "Bot Started: Type /start in Telegram trading bot channel."
    logging.info(start_msg)
    print(start_msg)

    # Schedule the market analysis job
    jq.run_repeating(analyse_market, interval=60, first=0)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
