"""
pull_btc_ohlc.py — long-history daily BTC *OHLC* for an honest (intrabar) backtest.

Source: Bitstamp BTC/USD daily OHLC (US-accessible, history back to ~2011-08), paginated.
We cross-check its close against the Coin Metrics PriceUSD series (btc_daily.csv) so we trust
the highs/lows before using them for stop/target fills. Covers all four halving epochs with
real intraday range (epoch 1's 2013 cycle from 2011-08 onward).
"""
import json
import time
import urllib.request
import pandas as pd

OUT = "btc_ohlc_daily.csv"
PAIR = "btcusd"
STEP = 86400          # daily
START = 1312156800    # 2011-08-01 UTC
LIMIT = 1000


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def main():
    print("fetching Bitstamp btcusd daily OHLC (paginated) ...")
    rows, start = [], START
    now = int(time.time())
    while start < now:
        url = (f"https://www.bitstamp.net/api/v2/ohlc/{PAIR}/"
               f"?step={STEP}&limit={LIMIT}&start={start}")
        d = _get(url)
        chunk = d.get("data", {}).get("ohlc", [])
        if not chunk:
            break
        rows.extend(chunk)
        last_ts = int(chunk[-1]["timestamp"])
        print(f"  +{len(chunk):4d} rows  through {pd.to_datetime(last_ts, unit='s').date()}")
        if last_ts <= start:
            break
        start = last_ts + STEP

    df = pd.DataFrame(rows)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date"] = pd.to_datetime(df["timestamp"].astype(int), unit="s").dt.normalize()
    df = df.rename(columns={"open": "o", "high": "h", "low": "l", "close": "c", "volume": "v"})
    df = df[["date", "o", "h", "l", "c", "v"]].dropna(subset=["c"])
    df = df[df["c"] > 0].drop_duplicates("date").sort_values("date").reset_index(drop=True)

    # cross-check close vs Coin Metrics PriceUSD
    try:
        cm = pd.read_csv("btc_daily.csv", parse_dates=["date"])
        m = df.merge(cm, on="date")
        m = m[(m["c"] > 0) & (m["close"] > 0)]
        rel = (m["c"] - m["close"]).abs() / m["close"]
        print(f"\n  cross-check vs Coin Metrics on {len(m)} overlapping days:")
        print(f"    median absdiff={rel.median()*100:.2f}%  p95={rel.quantile(.95)*100:.2f}%  "
              f"max={rel.max()*100:.1f}%")
    except FileNotFoundError:
        print("  (btc_daily.csv not found; skipping cross-check)")

    df.to_csv(OUT, index=False)
    print(f"\nrows={len(df)}  span {df['date'].min().date()} -> {df['date'].max().date()}")
    print(f"first: {df.iloc[0]['date'].date()} O{df.iloc[0]['o']:.2f} H{df.iloc[0]['h']:.2f} "
          f"L{df.iloc[0]['l']:.2f} C{df.iloc[0]['c']:.2f}")
    print(f"last:  {df.iloc[-1]['date'].date()} C{df.iloc[-1]['c']:,.0f}")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
