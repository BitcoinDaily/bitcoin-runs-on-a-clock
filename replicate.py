"""
replicate.py — robustness levers #1 and #5:
  (a) replicate the BTC result on the independent Coin Metrics close series (different source
      than Bitstamp -> guards against exchange-specific price artifacts), and
  (b) generalize to ETH (genesis 2015-07-30, Coin Metrics close).

Epoch boundaries stay at the BTC halving dates, read as the market-wide crypto cycle calendar
(ETH has no halving; crypto cycles are shared). Close-only series get Parts A (IC) and C
(exposure Sharpe-vs-B&H) — the two analyses that carry the paper's statistical weight. The
intrabar Part B needs real OHLC and is BTC/Bitstamp-only.
"""
import numpy as np
import pandas as pd
import pl_lib
from study_signals import fwd_return, spearman

EPOCH_NAME = {1: "E1_2013", 2: "E2_2017", 3: "E3_2021", 4: "E4_2025"}
SIGNALS = ["pl_z", "mayer_z", "rsi"]
ANN = 365.0

CHEAP = {
    "pl_z":    lambda d: d["pl_z"] < 0.0,
    "mayer_z": lambda d: d["mayer_z"] < 0.0,
    "rsi":     lambda d: d["rsi"] < 50.0,
}


def sharpe(ret):
    ret = ret.dropna()
    if len(ret) < 20 or ret.std() == 0:
        return np.nan
    return float(ret.mean() / ret.std() * np.sqrt(ANN))


def run_series(name, df):
    df = pl_lib.build_signals(df)
    df["ret"] = df["c"].pct_change()
    for k in [30, 180]:
        df[f"fwd{k}"] = fwd_return(df["c"].to_numpy(), k)

    n_fit = df["pl_n"].dropna()
    print(f"\n########## {name} ##########")
    print(f"  span {df.index.min().date()} -> {df.index.max().date()} ({len(df)}d)  "
          f"causal power-law exponent: first {n_fit.iloc[0]:.2f} -> latest {n_fit.iloc[-1]:.2f}")

    # ---- Part A: IC per epoch ----
    print(f"  IC (Spearman vs fwd ret):     30d{'':23}180d")
    print(f"  {'epoch':9} {'n':>5}  " + "  ".join(f"{s:>8}" for s in SIGNALS)
          + "   |  " + "  ".join(f"{s:>8}" for s in SIGNALS))
    for e in [1, 2, 3, 4]:
        sub = df[df["epoch"] == e]
        cells30, cells180, n = [], [], 0
        for h, cells in [(30, cells30), (180, cells180)]:
            for s in SIGNALS:
                d2 = sub.dropna(subset=[s, f"fwd{h}"])
                cells.append(f"{spearman(d2[s], d2[f'fwd{h}']):+.2f}" if len(d2) >= 60 else "  n/a")
                n = max(n, len(d2))
        if n == 0:
            continue
        print(f"  {EPOCH_NAME[e]:9} {n:>5}  " + "  ".join(f"{c:>8}" for c in cells30)
              + "   |  " + "  ".join(f"{c:>8}" for c in cells180))

    # ---- Part C: Sharpe edge vs buy&hold per epoch ----
    masks = {s: CHEAP[s](df).shift(1).fillna(False) for s in CHEAP}
    print(f"  Sharpe edge vs buy&hold (long/flat, causal 1d lag):")
    print(f"  {'epoch':9} {'B&H':>6}  " + "  ".join(f"{s:>8}" for s in SIGNALS))
    for e in [1, 2, 3, 4]:
        sub = df[df["epoch"] == e]
        if len(sub) < 200 or sub["pl_z"].notna().sum() < 100:
            continue
        bh = sharpe(sub["ret"])
        edges = []
        for s in SIGNALS:
            r = pd.Series(np.where(masks[s].loc[sub.index], sub["ret"], 0.0), index=sub.index)
            edges.append(f"{sharpe(r) - bh:+.2f}")
        print(f"  {EPOCH_NAME[e]:9} {bh:>+6.2f}  " + "  ".join(f"{c:>8}" for c in edges))


def main():
    # (a) BTC on the independent Coin Metrics series
    btc_cm = pl_lib.load_close_csv("btc_daily.csv", genesis=pl_lib.GENESIS)
    run_series("BTC (Coin Metrics, independent source)", btc_cm)

    # (b) ETH, its own genesis
    eth = pl_lib.load_close_csv("eth_daily.csv", genesis=pd.Timestamp("2015-07-30"))
    run_series("ETH (Coin Metrics, genesis 2015-07-30)", eth)


if __name__ == "__main__":
    main()
