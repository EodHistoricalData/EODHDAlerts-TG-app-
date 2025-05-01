# handlers.py

from telegram import Update
from telegram.ext import CallbackContext
from config import DEFAULT_SYMBOL, DEFAULT_INTERVAL
from data_fetcher import DataFetcher
from strategy import SMACrossoverStrategy
from telegram_notifier import TelegramNotifier

symbol = DEFAULT_SYMBOL
interval = DEFAULT_INTERVAL


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Trading Bot!")


def set_symbol(update: Update, context: CallbackContext):
    global symbol
    if context.args:
        symbol = context.args[0]
        update.message.reply_text(f"Symbol set to {symbol}")
    else:
        update.message.reply_text("Please provide a symbol.")


def set_interval(update: Update, context: CallbackContext):
    global interval
    if context.args:
        interval = context.args[0]
        update.message.reply_text(f"Interval set to {interval}")
    else:
        update.message.reply_text("Please provide an interval.")


def get_price(update: Update, context: CallbackContext):
    fetcher = DataFetcher(symbol, interval)
    price = fetcher.fetch_price()
    if price:
        update.message.reply_text(f"Current price of {symbol}: {price}")
    else:
        update.message.reply_text("Failed to fetch data.")


def analyse_market(context: CallbackContext):
    fetcher = DataFetcher(symbol, interval)
    data = fetcher.fetch_ohlc()
    if data.empty:
        return
    strategy = SMACrossoverStrategy(short_window=20, long_window=50)
    signals = strategy.generate_signals(data)
    latest_signal = signals["position"].iloc[-1]
    notifier = TelegramNotifier()

    if latest_signal == 1:
        notifier.send_message(f"Buy signal for {symbol}")
    elif latest_signal == -1:
        notifier.send_message(f"Sell signal for {symbol}")
