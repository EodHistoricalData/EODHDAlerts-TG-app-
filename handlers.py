# handlers.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from config import DEFAULT_SYMBOL, DEFAULT_INTERVAL
from data_fetcher import DataFetcher
from strategy import StrategyFactory
from telegram_notifier import TelegramNotifier

# Configure a logger for debugging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

symbol: str = DEFAULT_SYMBOL
interval: str = DEFAULT_INTERVAL
current_strategy_name: str = "sma"
strategy_params: dict = {}


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Trading Bot!")


def set_symbol(update: Update, context: CallbackContext) -> None:
    global symbol

    msg = update.effective_message

    if context.args:
        symbol = context.args[0].upper()
        msg.reply_text(f"Symbol set to {symbol}")
    else:
        msg.reply_text("Please provide a symbol.")


def set_interval(update: Update, context: CallbackContext) -> None:
    global interval

    msg = update.effective_message

    if context.args:
        interval = context.args[0]
        msg.reply_text(f"Interval set to {interval}")
    else:
        msg.reply_text("Please provide an interval.")


def get_price(update: Update, context: CallbackContext) -> None:
    fetcher = DataFetcher(symbol, interval)
    price = fetcher.fetch_price()

    msg = update.effective_message

    if price is not None:
        msg.reply_text(f"Current price of {symbol}: {price}")
    else:
        msg.reply_text("Failed to fetch data.")


def list_strategies(update: Update, context: CallbackContext) -> None:
    names = StrategyFactory.list_strategies()
    message = "Available strategies:\n" + "\n".join(f"- {n}" for n in names)
    update.message.reply_text(message)


def set_strategy(update: Update, context: CallbackContext) -> None:
    """
    /set_strategy [name]:
     - With an arg: set it immediately.
     - Without args: show inline buttons.
    """
    global current_strategy_name, strategy_params

    names = StrategyFactory.list_strategies()

    if context.args:
        name = context.args[0].lower()
        if name in names:
            current_strategy_name = name
            strategy_params = {}
            update.message.reply_text(f'Strategy set to "{name}".')
        else:
            update.message.reply_text(f'Unknown strategy "{name}".')
        return

    # No args: build an inline keyboard
    keyboard = [
        InlineKeyboardButton(text=nm.upper(), callback_data=f"setstrat:{nm}")
        for nm in names
    ]

    # Arrange two buttons per row
    rows = [keyboard[i : i + 2] for i in range(0, len(keyboard), 2)]
    reply_markup = InlineKeyboardMarkup(rows)
    update.message.reply_text("Please choose a strategy:", reply_markup=reply_markup)


def strategy_button(update: Update, context: CallbackContext) -> None:
    """Handle button clicks from the inline keyboard."""
    global current_strategy_name, strategy_params

    query = update.callback_query
    data = query.data or ""
    logger.info("Callback query received: %r", data)

    # Acknowledge the callback right away (stops the “loading…”)
    query.answer()

    if not data.startswith("setstrat:"):
        return

    _, name = data.split(":", 1)
    if name in StrategyFactory.list_strategies():
        current_strategy_name = name
        strategy_params = {}
        query.edit_message_text(f'Strategy set to "{name}".')
    else:
        query.edit_message_text(f'Unknown strategy "{name}".')


def current_strategy(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Current strategy: "{current_strategy_name}".')


def analyse_market(context: CallbackContext) -> None:
    fetcher = DataFetcher(symbol, interval)
    data = fetcher.fetch_ohlc()
    if data.empty:
        return

    strategy = StrategyFactory.create_strategy(current_strategy_name, **strategy_params)
    signals = strategy.generate_signals(data)
    latest_position = signals["position"].iloc[-1]
    notifier = TelegramNotifier()

    if latest_position == 1:
        notifier.send_message(f"Buy signal for {symbol}")
    elif latest_position == -1:
        notifier.send_message(f"Sell signal for {symbol}")
