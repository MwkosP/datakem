import yfinance as yf
import pandas as pd

def fetchAssetData(
    ticker: str,
    start: str | None = None,
    end: str | None = None,
    interval: str = "1d",
    preprocessing: str | None = None,  # Προσθήκη: None ή 'unfiltered'
) -> pd.DataFrame:
    """Fetch Open, High, Low, Close, and Volume data for a given asset."""
    historyOptions = {
        "start": start,
        "end": end,
        "interval": interval,
        "actions": False,
    }
    if start is None and end is None:
        historyOptions["period"] = "1y"

    asset = yf.Ticker(ticker)
    data = asset.history(
        **{key: value for key, value in historyOptions.items() if value is not None}
    )
    if data.empty:
        raise RuntimeError(f"No data was returned for {ticker}")
        
    # Επιλογή των στηλών που θέλεις
    data = data[["Open", "High", "Low", "Close", "Volume"]]
    
    # Αφαίρεση Timezone (απαραίτητο για Excel και reindex)
    if isinstance(data.index, pd.DatetimeIndex):
        data.index = data.index.tz_localize(None)
        
    # Εφαρμογή του preprocessing για εισαγωγή unfiltered NaN
    
    # Καθορισμός συχνότητας ανάλογα με το interval (π.χ. '1d' -> 'D', '1h' -> 'H')
    freq = "H" if "h" in interval or "m" in interval else "D"
    full_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq=freq)
    data = data.reindex(full_range)
        
    return data
