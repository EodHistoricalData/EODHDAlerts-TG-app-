# handlers.py

import logging
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes  # type: ignore
from config import DEFAULT_SYMBOL, DEFAULT_INTERVAL
from data_fetcher import DataFetcher
from strategy import StrategyFactory
from telegram_notifier import TelegramNotifier
from backtest import simulate_trades
from typing import Optional

# Configure a logger for debugging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

symbol: str = DEFAULT_SYMBOL
interval: str = DEFAULT_INTERVAL
current_strategy_name: str = "sma"
strategy_params: dict = {}
last_candle_time: Optional[pd.Timestamp] = None

debug_mode: bool = False


def interval_to_seconds(interval: str) -> int:
    mapping = {
        "1m": 60,
        "5m": 300,
        "h": 3600,
        "d": 86400,
        "w": 604800,
        "m": 2592000,
    }
    return mapping.get(interval, 60)  # fallback to 60 seconds


def get_latest_signal(strategy, data: pd.DataFrame) -> int:
    df = strategy.generate_signals(data)
    if "signal" not in df.columns or df.empty:
        return 0
    return int(df["signal"].iloc[-1])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Trading Bot!")


async def set_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global symbol
    msg = update.effective_message

    if context.args:
        symbol = context.args[0].upper()
        await msg.reply_text(f"Symbol set to {symbol}")
    else:
        await msg.reply_text("Please provide a symbol.")


async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global interval
    msg = update.effective_message

    if not context.args:
        await msg.reply_text("Please provide an interval (e.g., 1m, 5m, 1h, 1d).")
        return

    interval = context.args[0]

    # Reschedule job to match new interval
    job_queue = context.application.job_queue
    job_queue.scheduler.remove_all_jobs()

    seconds = interval_to_seconds(interval)
    job_queue.run_repeating(analyse_market, interval=seconds, first=0)

    await msg.reply_text(f"Interval set to {interval} and scheduler updated.")


async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fetcher = DataFetcher(symbol, interval)
    price = fetcher.fetch_price()

    msg = update.effective_message

    if price is not None:
        await msg.reply_text(f"Current price of {symbol}: {price}")
    else:
        await msg.reply_text("Failed to fetch data.")


async def list_strategies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    names = StrategyFactory.list_strategies()
    message = "Available strategies:\n" + "\n".join(f"- {n}" for n in names)
    await update.message.reply_text(message)


async def set_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_strategy_name, strategy_params

    names = StrategyFactory.list_strategies()

    if context.args:
        name = context.args[0].lower()
        if name in names:
            current_strategy_name = name
            strategy_params = {}
            await update.message.reply_text(f'Strategy set to "{name}".')
        else:
            await update.message.reply_text(f'Unknown strategy "{name}".')
        return

    # No args: build an inline keyboard
    keyboard = [
        InlineKeyboardButton(text=nm.upper(), callback_data=f"setstrat:{nm}")
        for nm in names
    ]
    rows = [keyboard[i : i + 2] for i in range(0, len(keyboard), 2)]
    reply_markup = InlineKeyboardMarkup(rows)
    await update.message.reply_text(
        "Please choose a strategy:", reply_markup=reply_markup
    )


async def strategy_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global current_strategy_name, strategy_params

    query = update.callback_query
    data = query.data or ""
    logger.info("Callback query received: %r", data)

    await query.answer()

    if not data.startswith("setstrat:"):
        return

    _, name = data.split(":", 1)
    if name in StrategyFactory.list_strategies():
        current_strategy_name = name
        strategy_params = {}
        await query.edit_message_text(f'Strategy set to "{name}".')
    else:
        await query.edit_message_text(f'Unknown strategy "{name}".')


async def current_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Current strategy: "{current_strategy_name}".')


async def toggle_debug(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global debug_mode

    if not context.args:
        await update.message.reply_text("Usage: /debug true or /debug false")
        return

    arg = context.args[0].lower()
    if arg == "true":
        debug_mode = True
        await update.message.reply_text("Debug mode enabled.")
    elif arg == "false":
        debug_mode = False
        await update.message.reply_text("Debug mode disabled.")
    else:
        await update.message.reply_text("Invalid option. Use true or false.")


async def analyse_market(context: ContextTypes.DEFAULT_TYPE) -> None:
    global last_candle_time

    fetcher = DataFetcher(symbol, interval)
    data = fetcher.fetch_ohlc()
    if data.empty:
        return

    strategy = StrategyFactory.create_strategy(current_strategy_name, **strategy_params)
    signal = get_latest_signal(strategy, data)
    notifier = TelegramNotifier()

    last_price = data["close"].iloc[-1]
    last_time_col = "datetime" if "datetime" in data.columns else "date"
    current_candle_time = data[last_time_col].iloc[-1]

    # Prevent duplicate processing of same candle
    if last_candle_time == current_candle_time:
        if debug_mode:
            await notifier.send_message(
                f"[DEBUG] Skipped - already processed candle at {current_candle_time}"
            )
        return

    # Update last seen timestamp
    last_candle_time = current_candle_time

    if debug_mode:
        await notifier.send_message(
            f"[DEBUG] analyse_market ran for {symbol} at price {last_price} (timestamp: {current_candle_time})"
        )

    if signal == 1:
        await notifier.send_message(
            f"Buy signal for {symbol} at {last_price} (timestamp: {current_candle_time})"
        )
    elif signal == -1:
        await notifier.send_message(
            f"Sell signal for {symbol} at {last_price} (timestamp: {current_candle_time})"
        )


async def backtest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "Usage: /backtest <strategy> <symbol> <interval>"
            )
            return

        strategy_name, symbol, interval = args[0], args[1], args[2]

        strategy = StrategyFactory.create_strategy(strategy_name)
        fetcher = DataFetcher(symbol=symbol, interval=interval)
        df = fetcher.fetch_ohlc()
        df = strategy.generate_signals(df)

        await update.message.reply_text(
            f"Signal value counts:\n{df['signal'].value_counts()}"
        )
        stats = simulate_trades(df)

        if stats["log"]:
            await update.message.reply_text(
                "\n".join(stats["log"][-10:])
            )  # last 10 trades

        msg = (
            f"Backtest result for {symbol} using {strategy_name.upper()} strategy:\n"
            f"- Trades: {stats['trades']}\n"
            f"- Wins: {stats['wins']}, Losses: {stats['losses']}\n"
            f"- Win Rate: {stats['win_rate_pct']}%\n"
            f"- Total Return: {stats['total_return_pct']}%\n"
            f"- Data points: {stats['data_points']}\n"
            f"- Period: {stats['start_time']} → {stats['end_time']}"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Backtest failed: {e}")
