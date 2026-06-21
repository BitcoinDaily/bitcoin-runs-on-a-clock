"""
pull_macro.py — macro/liquidity battery from FRED (free fredgraph.csv endpoint, no API key):
  M2SL     US M2 money stock (monthly, 1959-)          — the "liquidity" candidate
  WALCL    Fed balance sheet, total assets (weekly)     — QE/QT proxy
  NFCI     Chicago Fed financial conditions (weekly)    — business/credit-cycle proxy
  T10Y2Y   10y-2y Treasury spread (daily)               — classic business-cycle clock
  INDPRO   Industrial production (monthly)              — real business cycle

Each series is saved raw; the study script applies PUBLICATION LAGS so signals are causal
(you can't know April's M2 in April — it prints ~4 weeks later).
"""
import io
import urllib.request
import pandas as pd

SERIES = ["M2SL", "WALCL", "NFCI", "T10Y2Y", "INDPRO"]
OUT = "macro_fred.csv"


def fetch(sid):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
    raw = urllib.request.urlopen(req, timeout=120).read()
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = ["date", sid]
    df["date"] = pd.to_datetime(df["date"])
    df[sid] = pd.to_numeric(df[sid], errors="coerce")
    return df.set_index("date")


def main():
    frames = []
    for sid in SERIES:
        d = fetch(sid)
        v = d[sid].dropna()
        print(f"  {sid:8} {len(v):6d} obs  {v.index.min().date()} -> {v.index.max().date()}  "
              f"latest {v.iloc[-1]:,.2f}")
        frames.append(d)
    df = pd.concat(frames, axis=1).sort_index()
    df.to_csv(OUT)
    print(f"saved -> {OUT}  ({len(df)} rows)")


if __name__ == "__main__":
    main()
