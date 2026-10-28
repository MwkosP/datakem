import pandas as pd


def preprocessAssetData(
    data: pd.DataFrame,
    method: str,
    window: int = 5,
) -> pd.DataFrame:
    """Handle missing OHLCV values using the selected method."""
    if method == "keep":
        return data
    if method == "drop":
        return data.dropna()
    if method == "sma":
        averages = data.rolling(window=window, min_periods=1).mean()
        return data.fillna(averages).bfill()
    if method == "ema":
        averages = data.ewm(span=window, adjust=False, min_periods=1).mean()
        return data.fillna(averages).bfill()

    raise ValueError(f"Unknown missing-data method: {method}")
