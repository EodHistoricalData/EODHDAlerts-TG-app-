import pandas as pd


def simulate_trades(df: pd.DataFrame, fee: float = 0.001) -> dict:
    """Simulates trading using 'signal' and 'close' columns in the dataframe."""
    
    df = df.copy()
    df.dropna(subset=["close", "signal"], inplace=True)

    trades = []
    log = []
    entry_price = None
    in_position = False

    # Identify time column
    timestamp_col = None
    if "datetime" in df.columns:
        timestamp_col = "datetime"
    elif "date" in df.columns:
        timestamp_col = "date"

    for i, row in df.iterrows():
        time = row[timestamp_col] if timestamp_col else str(i)
        price = row["close"]
        signal = row["signal"]

        if signal == 1 and not in_position:
            entry_price = price
            in_position = True
            log.append(f"BUY at {price:.2f} on {time}")

        elif signal == -1 and in_position:
            exit_price = price
            pct_change = (exit_price - entry_price) / entry_price - fee
            trades.append(pct_change)
            log.append(
                f"SELL at {exit_price:.2f} on {time} (Return: {pct_change * 100:.2f}%)"
            )
            in_position = False
            entry_price = None

    total_return = sum(trades)
    num_trades = len(trades)
    wins = len([t for t in trades if t > 0])
    losses = len([t for t in trades if t <= 0])
    win_rate = wins / num_trades * 100 if num_trades > 0 else 0

    data_points = len(df)
    start_time = df[timestamp_col].iloc[0] if timestamp_col else None
    end_time = df[timestamp_col].iloc[-1] if timestamp_col else None

    return {
        "trades": num_trades,
        "total_return_pct": round(total_return * 100, 2),
        "win_rate_pct": round(win_rate, 2),
        "wins": wins,
        "losses": losses,
        "log": log,
        "data_points": data_points,
        "start_time": str(start_time),
        "end_time": str(end_time),
    }
