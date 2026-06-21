"""
study_signals.py — Part A: cross-cycle signal-quality decay (the paper's core result).

For each causal signal (power-law z, RSI-14, Mayer-z) measure its Information Coefficient =
Spearman rank correlation with FORWARD returns (30/90/180 day), computed *within each halving
epoch*. Mean-reversion signals should show NEGATIVE IC (high signal = stretched above trend =
lower forward return). The hypothesis: every signal's |IC| decays across epochs 1->4, and the
power-law signal decays the slowest (stays predictive deepest into Bitcoin's maturity).

Forward returns are used ONLY to score signals (never to build them) -> no leakage into signals.
"""
import numpy as np
import pandas as pd
import pl_lib


def spearman(a, b):
    """Spearman rank correlation via pandas ranks (no scipy dependency)."""
    a = pd.Series(np.asarray(a, float)); b = pd.Series(np.asarray(b, float))
    m = a.notna() & b.notna()
    if m.sum() < 3:
        return np.nan
    return a[m].rank().corr(b[m].rank())

HORIZONS = [30, 90, 180]
EPOCH_NAME = {1: "E1 2013cyc", 2: "E2 2017cyc", 3: "E3 2021cyc", 4: "E4 2025cyc"}
SIGNALS = ["pl_z", "mayer_z", "rsi"]


def fwd_return(c, k):
    c = np.asarray(c, float)
    f = np.full(len(c), np.nan)
    f[:-k] = c[k:] / c[:-k] - 1.0
    return f


def main():
    df = pl_lib.build_signals(pl_lib.load_prices())
    for k in HORIZONS:
        df[f"fwd{k}"] = fwd_return(df["c"].to_numpy(), k)

    print(f"data: {df.index.min().date()} -> {df.index.max().date()}  ({len(df)} days)")
    # sanity: causal power-law exponent should settle in the well-known ~5-6 range
    n_now = df["pl_n"].dropna()
    print(f"causal power-law exponent n_t: first valid {n_now.iloc[0]:.2f}  "
          f"latest {n_now.iloc[-1]:.2f}  (literature ~5.8)")
    print(f"latest signals  pl_z={df['pl_z'].iloc[-1]:+.2f}  "
          f"mayer_z={df['mayer_z'].iloc[-1]:+.2f}  rsi={df['rsi'].iloc[-1]:.0f}")

    print("\n================ INFORMATION COEFFICIENT (Spearman signal vs forward return) "
          "================")
    print("negative IC = mean-reverting as expected (stretched-high -> lower forward return); "
          "|IC| = strength\n")

    for k in HORIZONS:
        fcol = f"fwd{k}"
        print(f"--- forward {k}d return ---")
        header = "  epoch        n   " + "  ".join(f"{s:>9}" for s in SIGNALS)
        print(header)
        rows_by_epoch = {}
        for e in [1, 2, 3, 4]:
            sub = df[(df["epoch"] == e)].dropna(subset=[fcol])
            cells, ncell = [], 0
            line = f"  {EPOCH_NAME[e]:11}"
            for s in SIGNALS:
                d2 = sub.dropna(subset=[s])
                if len(d2) < 30:
                    cells.append(("nan", 0)); continue
                ic = spearman(d2[s], d2[fcol])
                cells.append((f"{ic:+.2f}", len(d2)))
                ncell = max(ncell, len(d2))
            line = f"  {EPOCH_NAME[e]:11} {ncell:5d}  " + "  ".join(f"{c[0]:>9}" for c in cells)
            print(line)
            rows_by_epoch[e] = {s: cells[i][0] for i, s in enumerate(SIGNALS)}
        # decay summary: |IC| epoch4 vs epoch1
        print("  decay |IC| E1->E4:", end=" ")
        for s in SIGNALS:
            try:
                ic1 = abs(float(rows_by_epoch[1][s])); ic4 = abs(float(rows_by_epoch[4][s]))
                ret = f"{s} {ic1:.2f}->{ic4:.2f} ({(ic4-ic1)/ic1*100:+.0f}%)"
            except (ValueError, ZeroDivisionError):
                ret = f"{s} n/a"
            print(ret, end="   ")
        print("\n")


if __name__ == "__main__":
    main()
