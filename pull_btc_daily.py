"""
pull_btc_daily.py — long-history daily BTC for the power-law study.

Primary source: Coin Metrics community data (free, public), BTC daily, PriceUSD back to
2010-07-18 — the cleanest long-history daily reference, covering all four halving epochs.
We keep only [date, PriceUSD] and cache to btc_daily.csv.

Fallback: CoinGecko market_chart (daily) from 2013-04-28 if Coin Metrics is unreachable.
"""
import io
import sys
import urllib.request
import pandas as pd

OUT = "btc_daily.csv"
CM_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv"


def _get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def from_coinmetrics():
    print(f"fetching Coin Metrics btc.csv ...")
    raw = _get(CM_URL)
    print(f"  got {len(raw)/1e6:.1f} MB")
    df = pd.read_csv(io.BytesIO(raw), usecols=["time", "PriceUSD"])
    df = df.rename(columns={"time": "date", "PriceUSD": "close"}).dropna(subset=["close"])
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    df = df[df["close"] > 0].sort_values("date").reset_index(drop=True)
    return df[["date", "close"]]


def main():
    try:
        df = from_coinmetrics()
        src = "coinmetrics"
    except Exception as e:
        print(f"Coin Metrics failed ({e}); trying CoinGecko ...")
        # CoinGecko fallback: max daily history
        url = ("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
               "?vs_currency=usd&days=max&interval=daily")
        import json
        d = json.loads(_get(url))
        px = pd.DataFrame(d["prices"], columns=["ms", "close"])
        px["date"] = pd.to_datetime(px["ms"], unit="ms").dt.normalize()
        df = px.groupby("date", as_index=False)["close"].last()
        src = "coingecko"

    df.to_csv(OUT, index=False)
    print(f"\nsource={src}  rows={len(df)}")
    print(f"span: {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"first: {df.iloc[0]['date'].date()} ${df.iloc[0]['close']:.4f}")
    print(f"last:  {df.iloc[-1]['date'].date()} ${df.iloc[-1]['close']:,.0f}")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
