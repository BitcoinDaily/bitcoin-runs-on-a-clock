"""
pull_btc_metrics.py — extended Coin Metrics pull: price + the on-chain series needed for the
famous cycle-caller indicators (MVRV ratio; daily issuance USD for the Puell Multiple).
Saves btc_metrics.csv with whatever of the candidate columns exist.
"""
import io
import urllib.request
import pandas as pd

OUT = "btc_metrics.csv"
CM_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv"
WANT = ["time", "PriceUSD", "CapMVRVCur", "IssTotUSD", "RevUSD", "IssTotNtv",
        "CapMrktCurUSD", "CapRealUSD"]


def main():
    print("fetching Coin Metrics btc.csv (full) ...")
    req = urllib.request.Request(CM_URL, headers={"User-Agent": "Mozilla/5.0 (research)"})
    raw = urllib.request.urlopen(req, timeout=180).read()
    print(f"  got {len(raw)/1e6:.1f} MB")
    head = pd.read_csv(io.BytesIO(raw), nrows=0)
    cols = [c for c in WANT if c in head.columns]
    missing = [c for c in WANT if c not in head.columns]
    print(f"  available: {cols}")
    if missing:
        print(f"  missing:   {missing}")
    df = pd.read_csv(io.BytesIO(raw), usecols=cols)
    df = df.rename(columns={"time": "date"})
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None).dt.normalize()
    df = df.dropna(subset=["PriceUSD"]).sort_values("date").reset_index(drop=True)

    # MVRV: prefer the precomputed column, else market/realized cap ratio
    if "CapMVRVCur" not in df and {"CapMrktCurUSD", "CapRealUSD"} <= set(df.columns):
        df["CapMVRVCur"] = df["CapMrktCurUSD"] / df["CapRealUSD"]
    # issuance USD for Puell: prefer IssTotUSD, else native issuance * price, else RevUSD
    if "IssTotUSD" not in df:
        if "IssTotNtv" in df:
            df["IssTotUSD"] = df["IssTotNtv"] * df["PriceUSD"]
        elif "RevUSD" in df:
            df["IssTotUSD"] = df["RevUSD"]
            print("  NOTE: using RevUSD (incl. fees) as Puell numerator — label in paper")

    df.to_csv(OUT, index=False)
    print(f"rows={len(df)}  span {df['date'].min().date()} -> {df['date'].max().date()}")
    for c in ["CapMVRVCur", "IssTotUSD"]:
        if c in df:
            v = df[c].dropna()
            print(f"  {c}: {len(v)} non-null, first {v.index[0]} latest {v.iloc[-1]:,.2f}")
    print(f"saved -> {OUT}")


if __name__ == "__main__":
    main()
