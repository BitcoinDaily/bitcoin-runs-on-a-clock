"""
pull_eth_daily.py — long-history daily ETH close (Coin Metrics PriceUSD, back to 2015-08)
for the generalization test: does the BTC maturation result replicate on a second asset?
Close-only -> used for the IC and exposure studies (no intrabar backtest on this).
"""
import io
import urllib.request
import pandas as pd

OUT = "eth_daily.csv"
CM_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/eth.csv"


def main():
    print("fetching Coin Metrics eth.csv ...")
    req = urllib.request.Request(CM_URL, headers={"User-Agent": "Mozilla/5.0 (research)"})
    raw = urllib.request.urlopen(req, timeout=120).read()
    print(f"  got {len(raw)/1e6:.1f} MB")
    df = pd.read_csv(io.BytesIO(raw), usecols=["time", "PriceUSD"])
    df = df.rename(columns={"time": "date", "PriceUSD": "close"}).dropna(subset=["close"])
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    df = df[df["close"] > 0].sort_values("date").reset_index(drop=True)
    df[["date", "close"]].to_csv(OUT, index=False)
    print(f"rows={len(df)}  span {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"first: {df.iloc[0]['date'].date()} ${df.iloc[0]['close']:.4f}   "
          f"last: {df.iloc[-1]['date'].date()} ${df.iloc[-1]['close']:,.0f}")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
