"""
clock_bottom_anchor_null.py — the PROPER null for the bottom anchor question, matching the
paper's empirical_null_test machinery: circular block-bootstrap of BTC log returns, real halving
calendar, identical mechanical turn rule, SELECTION-SYMMETRIC scoring (null paths get the
best-3-subset freedom), across all five block lengths L in {30,60,90,120,250}, B=2000 each.

Scores the BOTTOM cluster two ways and reports how often a random path reproduces the observed
tightness:
  (A) AFTER-TOP        : days from the cycle top to the bottom        (observed 3-range = 42d)  -> reproduces paper's bottom number
  (B) UNTIL-NEXT-HALVING: days from the bottom to the next halving     (observed 3-range = 29d)  -> the new anchor
"""
import numpy as np
import pandas as pd
import pl_lib
from empirical_null_test import extract_tops

H = dict(pl_lib.HALVINGS)
H[5] = pd.Timestamp("2028-04-15")
HALV = [H[i] for i in sorted(H)]

OBS_AFTERTOP = 42      # 406/364/366
OBS_UNTIL = 29         # 542/513/528
LS = [30, 60, 90, 120, 250]
B = 2000
SEED = 11


def best3_range(vals):
    """Min range over all 3-subsets (selection-symmetric: null gets the same freedom we had)."""
    v = sorted(vals)
    if len(v) < 3:
        return np.inf
    return min(v[i + 2] - v[i] for i in range(len(v) - 2))


def main():
    df = pl_lib.load_prices()
    c0 = df["c"].to_numpy()
    dates = df.index
    ret = np.diff(np.log(c0))
    n = len(ret)
    # days-until-next-halving per bar (real calendar; uses H5 estimate for post-2024 bars)
    nxt = np.array([min([(h - d).days for h in HALV if h > d], default=np.nan) for d in dates],
                   float)

    def path_scores(c):
        tops = extract_tops(c)
        if len(tops) < 2:
            return np.inf, np.inf
        bots = [tops[k] + int(np.argmin(c[tops[k]:tops[k + 1]])) for k in range(len(tops) - 1)]
        if len(bots) < 3:
            return np.inf, np.inf
        aftertop = [bots[k] - tops[k] for k in range(len(bots))]
        until = [nxt[b] for b in bots if not np.isnan(nxt[b])]
        return best3_range(aftertop), (best3_range(until) if len(until) >= 3 else np.inf)

    # self-check on the real series
    ra, ru = None, None
    print(f"observed: after-top best-3 range = {OBS_AFTERTOP}d, until-next-halving best-3 range = {OBS_UNTIL}d\n")
    print(f"  {'L':>5} {'B:after-top<=42d':>18} {'B:until-next<=29d':>18}")
    rng = np.random.default_rng(SEED)
    tot_at = tot_un = 0
    for L in LS:
        nb = int(np.ceil(n / L))
        hit_at = hit_un = 0
        for _ in range(B):
            starts = rng.integers(0, n, nb)
            idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
            cp = np.empty(n + 1); cp[0] = 1.0
            np.cumsum(ret[idx], out=cp[1:]); np.exp(cp[1:], out=cp[1:])
            at, un = path_scores(cp)
            hit_at += at <= OBS_AFTERTOP
            hit_un += un <= OBS_UNTIL
        tot_at += hit_at; tot_un += hit_un
        print(f"  {L:>5} {hit_at/B*100:>17.2f}% {hit_un/B*100:>17.2f}%")
    print(f"\n  pooled: after-top {tot_at}/{len(LS)*B} ({tot_at/(len(LS)*B)*100:.2f}%)  |  "
          f"until-next-halving {tot_un}/{len(LS)*B} ({tot_un/(len(LS)*B)*100:.2f}%)")
    print("  (after-top should land near the paper's locked 31-43%; until-next is the new anchor)")


if __name__ == "__main__":
    main()
