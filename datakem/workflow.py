import argparse
from pathlib import Path

from .data.fetch_data import fetchAssetData


OUTPUT_FILE = Path(__file__).with_name("btc_daily.xlsx")
ASSETS = ("BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD")


def runWorkflow(selectedAsset: str = "BTC-USD") -> None:
    data = fetchAssetData(selectedAsset)
    data.to_excel(OUTPUT_FILE, sheet_name="Data")
    print(f"Saved {len(data)} {selectedAsset} records to {OUTPUT_FILE.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build the asset dashboard")
    parser.add_argument("--asset", choices=ASSETS, default="BTC-USD")
    arguments = parser.parse_args()
    runWorkflow(arguments.asset)
