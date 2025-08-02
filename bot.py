# bot.py

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    backtest,
    start,
    interval_to_seconds,
    interval,
    set_symbol,
    set_interval,
    get_price,
    list_strategies,
    set_strategy,
    strategy_button,
    current_strategy,
    analyse_market,
    toggle_debug,
)

# Set up root logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


# Called once on bot startup
async def on_startup(app):
    logging.info("Bot Started: Type /start in Telegram trading bot channel.")

    seconds = interval_to_seconds(interval)
    app.job_queue.run_repeating(analyse_market, interval=seconds, first=0)


def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set_symbol", set_symbol))
    application.add_handler(CommandHandler("set_interval", set_interval))
    application.add_handler(CommandHandler("get_price", get_price))
    application.add_handler(CommandHandler("list_strategies", list_strategies))
    application.add_handler(CommandHandler("set_strategy", set_strategy))
    application.add_handler(CommandHandler("current_strategy", current_strategy))
    application.add_handler(CommandHandler("backtest", backtest))
    application.add_handler(CommandHandler("debug", toggle_debug))

    application.add_handler(
        CallbackQueryHandler(strategy_button, pattern=r"^setstrat:")
    )

    # Hook for startup logic (e.g. scheduling)
    application.post_init = on_startup
    application.run_polling()


if __name__ == "__main__":
    main()
