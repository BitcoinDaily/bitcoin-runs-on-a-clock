"""
exposure_study.py — all-days test of whether each signal's TIMING adds risk-adjusted value,
and whether that value persists across cycles. Complements the (necessarily thin) discrete-trade
backtest: here every day participates, so per-epoch Sharpe is statistically meaningful.

Each signal defines a daily long/flat exposure: LONG when "cheap" (below trend / oversold), else
FLAT. Exposure is shifted one day (causal: decide on close, hold from next day). We report, per
epoch and train/test, the strategy's annualized Sharpe / CAGR / maxDD / time-in-market vs the
always-long buy&hold benchmark. The question: does power-law-deviation timing keep beating
buy&hold's risk-adjusted return deeper into BTC's maturity than RSI does?
"""
import numpy as np
import pandas as pd
import pl_lib

ANN = 365.0  # crypto trades daily

# "cheap" (=long) condition per signal
CHEAP = {
    "pl_z":    lambda d: d["pl_z"] < 0.0,
    "mayer_z": lambda d: d["mayer_z"] < 0.0,
    "rsi":     lambda d: d["rsi"] < 50.0,
}


def stats(ret):
    ret = ret.dropna()
    if len(ret) < 20 or ret.std() == 0:
        return dict(n=len(ret), sharpe=np.nan, cagr=np.nan, maxdd=np.nan, tim=np.nan)
    eq = (1 + ret).cumprod()
    dd = (eq / eq.cummax() - 1).min()
    yrs = len(ret) / ANN
    cagr = eq.iloc[-1] ** (1 / yrs) - 1 if eq.iloc[-1] > 0 else -1
    sharpe = ret.mean() / ret.std() * np.sqrt(ANN)
    return dict(n=len(ret), sharpe=sharpe, cagr=cagr, maxdd=dd)


def main():
    df = pl_lib.build_signals(pl_lib.load_prices())
    df["ret"] = df["c"].pct_change()
    df["year"] = df.index.year

    masks = {s: CHEAP[s](df).shift(1).fillna(False) for s in CHEAP}  # causal: hold from next day
    df["bh"] = df["ret"]
    for s in CHEAP:
        df[f"r_{s}"] = np.where(masks[s], df["ret"], 0.0)
        df[f"in_{s}"] = masks[s].astype(float)

    def block(sub, label):
        bh = stats(sub["bh"])
        print(f"\n  {label}  ({sub.index.min().date()}..{sub.index.max().date()}, {len(sub)}d)")
        print(f"    {'buy&hold':10} Sharpe={bh['sharpe']:+5.2f}  CAGR={bh['cagr']*100:+7.1f}%  "
              f"maxDD={bh['maxdd']*100:+6.1f}%  tim=100%")
        for s in CHEAP:
            st = stats(sub[f"r_{s}"])
            tim = sub[f"in_{s}"].mean() * 100
            edge = (st['sharpe'] - bh['sharpe'])
            print(f"    {s:10} Sharpe={st['sharpe']:+5.2f}  CAGR={st['cagr']*100:+7.1f}%  "
                  f"maxDD={st['maxdd']*100:+6.1f}%  tim={tim:4.0f}%   "
                  f"Sharpe vs B&H: {edge:+.2f}")

    print(f"period {df.index.min().date()} -> {df.index.max().date()} ({len(df)}d)  "
          f"ann={ANN:.0f}, long/flat, causal 1d lag")
    print("=" * 78)
    block(df, "FULL SAMPLE")
    block(df[df["year"] < 2025], "TRAIN (pre-2025)")
    block(df[df["year"] >= 2025], "TEST (2025-2026)")
    print("\n" + "=" * 78 + "\n  PER-EPOCH (Sharpe edge vs buy&hold is the cross-cycle decay test)")
    for e in [1, 2, 3, 4]:
        sub = df[df["epoch"] == e]
        if len(sub) > 20:
            block(sub, f"EPOCH {e}")


if __name__ == "__main__":
    main()
