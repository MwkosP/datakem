from datakem.ui.runUi import runUi
from datakem.data import fetchAssetData
import pandas as pd
import yfinance as yf

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)





def main() -> None:
    #data = fetchAssetData("TSLA")
    #print(data)
    runUi()
    # 1. Download your data

    #df = yf.download("AAPL", start="2026-01-01", end="2026-10-01",)
    #asset = yf.Ticker("AAPL")
    # print(asset)

if __name__ == "__main__":
    main()