"""
ic_significance.py — referee-grade significance tests for the per-epoch Information Coefficients.

The statistical trap: an h-day forward return series is overlapping, hence MA(h-1) autocorrelated,
so a naive correlation t-stat overstates significance by roughly sqrt(h). Two independent
corrections, reported side by side:

  1. Newey-West (HAC) t-stat — regress standardized rank(fwd ret) on standardized rank(signal);
     the OLS slope IS the Spearman IC; Bartlett-kernel HAC standard error with lag = h.
  2. Circular moving-block bootstrap — resample (signal, fwd-ret) day-pairs in contiguous blocks
     of length L = min(h, n//5) (so >= 5 blocks), B = 2000; report the 95% CI and two-sided p.

Plus the PAIRED contrast the paper actually claims: delta = |IC_pl_z| - |IC_rsi| computed inside
identical bootstrap resamples — is the power-law signal's advantage over RSI itself significant,
epoch by epoch? (Testing each IC vs zero is not enough; the headline is the CONTRAST.)
"""
import numpy as np
import pandas as pd
import pl_lib
from study_signals import fwd_return

HORIZONS = [30, 90, 180]
SIGNALS = ["pl_z", "mayer_z", "rsi"]
EPOCH_NAME = {1: "E1_2013", 2: "E2_2017", 3: "E3_2021", 4: "E4_2025"}
B = 2000
SEED = 7


def _std_ranks(x):
    """Standardized ordinal ranks (mean 0, sd 1). Pearson of these = Spearman."""
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(1, len(x) + 1, dtype=float)
    r -= r.mean()
    s = r.std()
    return r / (s if s > 0 else 1.0)


def spearman_fast(a, b):
    return float(np.mean(_std_ranks(a) * _std_ranks(b)))


def nw_tstat(sig, fwd, lag):
    """Spearman IC + Newey-West (Bartlett, given lag) t-stat via rank-on-rank OLS."""
    x = _std_ranks(sig); y = _std_ranks(fwd)
    n = len(x)
    beta = float(np.mean(x * y))          # slope of y on x with var(x)=1  == Spearman IC
    u = y - beta * x
    g = x * u                              # score series
    lag = min(lag, n - 2)
    omega = float(np.mean(g * g))
    for j in range(1, lag + 1):
        w = 1.0 - j / (lag + 1.0)
        omega += 2.0 * w * float(np.mean(g[j:] * g[:-j]))
    se = np.sqrt(max(omega, 1e-12) / n)
    return beta, beta / se


def block_boot(sig_arrays, fwd, L, rng, B=B):
    """Circular moving-block bootstrap. Returns {signal: boot IC array} plus paired
    |IC_pl|-|IC_rsi| and |IC_pl|-|IC_mayer| arrays computed on the SAME resamples."""
    n = len(fwd)
    nb = int(np.ceil(n / L))
    out = {k: np.empty(B) for k in sig_arrays}
    d_rsi = np.empty(B); d_mayer = np.empty(B)
    for b in range(B):
        starts = rng.integers(0, n, nb)
        idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
        f = fwd[idx]
        ics = {k: spearman_fast(v[idx], f) for k, v in sig_arrays.items()}
        for k in out:
            out[k][b] = ics[k]
        d_rsi[b] = abs(ics["pl_z"]) - abs(ics["rsi"])
        d_mayer[b] = abs(ics["pl_z"]) - abs(ics["mayer_z"])
    return out, d_rsi, d_mayer


def boot_p(boot):
    """Two-sided percentile p-value vs zero."""
    return min(1.0, 2.0 * min((boot <= 0).mean(), (boot >= 0).mean()))


def main():
    rng = np.random.default_rng(SEED)
    df = pl_lib.build_signals(pl_lib.load_prices())
    for k in HORIZONS:
        df[f"fwd{k}"] = fwd_return(df["c"].to_numpy(), k)

    print(f"data {df.index.min().date()} -> {df.index.max().date()}  B={B} bootstrap, "
          f"NW lag = horizon, block L = min(h, n//5)")
    for h in HORIZONS:
        print(f"\n================ horizon {h}d ================")
        print(f"  {'epoch':8} {'n':>5}  {'signal':8} {'IC':>6} {'NW-t':>6}  "
              f"{'boot 95% CI':>16} {'p':>6}")
        for e in [1, 2, 3, 4]:
            sub = df[df["epoch"] == e].dropna(subset=SIGNALS + [f"fwd{h}"])
            n = len(sub)
            if n < 60:
                print(f"  {EPOCH_NAME[e]:8} {n:>5}  (too few joint obs)"); continue
            fwd = sub[f"fwd{h}"].to_numpy()
            sigs = {s: sub[s].to_numpy() for s in SIGNALS}
            L = max(10, min(h, n // 5))
            boots, d_rsi, d_mayer = block_boot(sigs, fwd, L, rng)
            for s in SIGNALS:
                ic, t = nw_tstat(sigs[s], fwd, lag=h)
                lo, hi = np.percentile(boots[s], [2.5, 97.5])
                p = boot_p(boots[s])
                star = " **" if (abs(t) >= 2 and p <= 0.05) else ("  *" if p <= 0.10 else "")
                print(f"  {EPOCH_NAME[e]:8} {n:>5}  {s:8} {ic:+.2f} {t:+6.2f}  "
                      f"[{lo:+.2f},{hi:+.2f}] {p:6.3f}{star}")
            for tag, d in [("pl-rsi", d_rsi), ("pl-mayer", d_mayer)]:
                lo, hi = np.percentile(d, [2.5, 97.5])
                p = boot_p(d)
                star = " **" if p <= 0.05 else ("  *" if p <= 0.10 else "")
                print(f"  {'':8} {'':>5}  D|IC| {tag:9} {d.mean():+.2f}      "
                      f"[{lo:+.2f},{hi:+.2f}] {p:6.3f}{star}")
            print()


if __name__ == "__main__":
    main()
