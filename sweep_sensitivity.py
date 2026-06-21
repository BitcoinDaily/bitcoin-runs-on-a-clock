"""
sweep_sensitivity.py — robustness lever #2: is the cross-cycle contrast knife-edge on any
parameter choice? Pre-registered grid (no cherry-picking afterward — every cell gets printed):

  1. HORIZON sweep      : pl_z IC at h = 60/90/120/180/240/360, per mature epoch (E2-E4)
  2. FIT-PARAM sweep    : power-law fit warmup {180,365,730} x z-score warmup {90,180,365},
                          IC@180 per epoch (9 variants)
  3. COMPARATOR sweep   : RSI period {7,14,21,30} IC@30 & @180; Mayer SMA {100,200,300} IC@180
  4. EXPOSURE-THRESHOLD : long/flat threshold sweep -> Sharpe edge vs B&H per epoch
                          (pl_z & mayer_z thr in {-0.25, 0, +0.25}; rsi thr in {40,50,60})

The claim being stress-tested: pl-deviation IC stays negative (mean-reverting) and its E4
Sharpe edge stays >= 0 across the grid, while RSI's E4 IC stays ~0 regardless of period.
E1 excluded (documented warmup artifact).
"""
import numpy as np
import pandas as pd
import pl_lib
from study_signals import fwd_return, spearman

EPOCHS = [2, 3, 4]
ANN = 365.0


def sharpe(ret):
    ret = pd.Series(ret).dropna()
    if len(ret) < 20 or ret.std() == 0:
        return np.nan
    return float(ret.mean() / ret.std() * np.sqrt(ANN))


def ic_cells(df, col, h):
    out = []
    for e in EPOCHS:
        sub = df[df["epoch"] == e].dropna(subset=[col, f"fwd{h}"])
        out.append(spearman(sub[col], sub[f"fwd{h}"]) if len(sub) >= 60 else np.nan)
    return out


def fmt(cells):
    return "  ".join(f"{c:+.2f}" if np.isfinite(c) else "  n/a" for c in cells)


def main():
    df = pl_lib.load_prices()
    df["epoch"] = pl_lib.epoch_of(df.index)
    horizons = [60, 90, 120, 180, 240, 360]
    for h in set(horizons) | {30}:
        df[f"fwd{h}"] = fwd_return(df["c"].to_numpy(), h)
    df["ret"] = df["c"].pct_change()

    # default signals
    base = pl_lib.build_signals(pl_lib.load_prices())
    for col in ["pl_z", "mayer_z", "rsi"]:
        df[col] = base[col]

    print("epochs: E2(2017cyc)  E3(2021cyc)  E4(2025cyc)\n")

    print("== 1. HORIZON sweep — pl_z IC (default fit) ==")
    print(f"   {'h':>4}   E2     E3     E4")
    for h in horizons:
        print(f"   {h:>4}  {fmt(ic_cells(df, 'pl_z', h))}")

    print("\n== 2. FIT-PARAM sweep — pl_z IC@180 ==")
    print(f"   {'fit_mo':>6} {'z_mo':>5}   E2     E3     E4")
    for mo_fit in [180, 365, 730]:
        _, _, r = pl_lib.causal_powerlaw(df, min_obs=mo_fit)
        for mo_z in [90, 180, 365]:
            df["_z"] = pl_lib.expanding_z(r, min_obs=mo_z)
            print(f"   {mo_fit:>6} {mo_z:>5}  {fmt(ic_cells(df, '_z', 180))}")

    print("\n== 3a. RSI period sweep — IC@30 | IC@180 ==")
    print(f"   {'n':>4}   E2     E3     E4    |   E2     E3     E4")
    for n in [7, 14, 21, 30]:
        df["_rsi"] = pl_lib.wilder_rsi(df["c"].to_numpy(), n)
        print(f"   {n:>4}  {fmt(ic_cells(df, '_rsi', 30))}  |  {fmt(ic_cells(df, '_rsi', 180))}")

    print("\n== 3b. Mayer SMA-window sweep — IC@180 ==")
    print(f"   {'sma':>4}   E2     E3     E4")
    for n in [100, 200, 300]:
        mayer = np.log(df["c"].to_numpy() / pl_lib.sma(df["c"].to_numpy(), n))
        df["_my"] = pl_lib.expanding_z(mayer)
        print(f"   {n:>4}  {fmt(ic_cells(df, '_my', 180))}")

    print("\n== 4. EXPOSURE-THRESHOLD sweep — Sharpe edge vs B&H per epoch ==")
    print(f"   {'signal':22}  E2     E3     E4")
    grids = ([("pl_z", t, lambda d, t=t: d["pl_z"] < t) for t in (-0.25, 0.0, 0.25)]
             + [("mayer_z", t, lambda d, t=t: d["mayer_z"] < t) for t in (-0.25, 0.0, 0.25)]
             + [("rsi", t, lambda d, t=t: d["rsi"] < t) for t in (40, 50, 60)])
    for name, thr, cond in grids:
        mask = cond(df).shift(1).fillna(False)
        cells = []
        for e in EPOCHS:
            sub = df[df["epoch"] == e]
            bh = sharpe(sub["ret"])
            r = np.where(mask.loc[sub.index], sub["ret"], 0.0)
            cells.append(sharpe(r) - bh)
        print(f"   {name:8} thr {thr:>5}    {fmt(cells)}")


if __name__ == "__main__":
    main()
