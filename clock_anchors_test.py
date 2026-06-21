"""
clock_anchors_test.py — the three clocks. For every cycle turn, measure it three ways:
  (1) days AFTER the most recent halving      (the indicator's CLOCK)
  (2) days from the previous turn             (top->bottom = days-after-top; bottom->top = days-after-bottom)
  (3) days UNTIL the next halving             (a forward countdown)
Report which anchor is tightest for tops vs bottoms, whether the anchors AGREE on the 2026
bottom window, and run the drawdown-process null on the tightest bottom anchor to see if its
tightness is real clock-lock or just how crashes play out.
"""
import numpy as np
import pandas as pd
import pl_lib

DAY = pd.Timedelta(days=1)
H = dict(pl_lib.HALVINGS)            # H1..H4
H[5] = pd.Timestamp("2028-04-15")    # estimate; drifts
halv = [H[i] for i in sorted(H)]

# locked mechanical turns (from cycle_callers.py)
TOPS = {2013: "2013-12-04", 2017: "2017-12-16", 2021: "2021-11-08", 2025: "2025-10-06"}
BOTS = {2015: "2015-01-14", 2018: "2018-12-15", 2022: "2022-11-09"}
TOPS = {k: pd.Timestamp(v) for k, v in TOPS.items()}
BOTS = {k: pd.Timestamp(v) for k, v in BOTS.items()}


def prev_halving(d):
    return max([h for h in halv if h <= d], default=None)


def next_halving(d):
    return min([h for h in halv if h > d], default=None)


def rng_days(vals):
    vals = [v for v in vals if v is not None]
    return max(vals) - min(vals), vals


print("THE THREE CLOCKS  (days for each turn under each anchor)")
print("=" * 78)

# ---- TOPS ----
print("\nTOPS")
print(f"  {'top':>6} {'after halving':>14} {'until next halv':>16} {'after prev bottom':>18}")
t_after, t_until, t_afterbot = [], [], []
sorted_bots = sorted(BOTS.values())
for yr, d in TOPS.items():
    ah = (d - prev_halving(d)).days
    un = (next_halving(d) - d).days if next_halving(d) is not None else None
    pb = [b for b in sorted_bots if b < d]
    ab = (d - pb[-1]).days if pb else None
    if yr != 2013:  # mature only for the after-halving headline
        t_after.append(ah); t_until.append(un)
    if ab is not None and yr != 2013:
        t_afterbot.append(ab)
    print(f"  {yr:>6} {ah:>14} {str(un):>16} {str(ab):>18}")
print(f"  mature range:  after-halving {rng_days(t_after)[0]:>3}d   "
      f"until-next {rng_days(t_until)[0]:>3}d   after-prev-bottom {rng_days(t_afterbot)[0]:>3}d")

# ---- BOTTOMS ----
print("\nBOTTOMS")
print(f"  {'bottom':>6} {'after halving':>14} {'until next halv':>16} {'after prev top':>15}")
b_after, b_until, b_aftertop = [], [], []
sorted_tops = sorted(TOPS.values())
for yr, d in BOTS.items():
    ah = (d - prev_halving(d)).days
    un = (next_halving(d) - d).days if next_halving(d) is not None else None
    pt = [t for t in sorted_tops if t < d]
    at = (d - pt[-1]).days if pt else None
    b_after.append(ah); b_until.append(un); b_aftertop.append(at)
    print(f"  {yr:>6} {ah:>14} {str(un):>16} {str(at):>15}")
print(f"  range:         after-halving {rng_days(b_after)[0]:>3}d   "
      f"until-next {rng_days(b_until)[0]:>3}d   after-top {rng_days(b_aftertop)[0]:>3}d")

# ---- do the anchors AGREE on the 2026 bottom? ----
print("\nDO THE ANCHORS AGREE ON THE 2026 BOTTOM?")
top25 = TOPS[2025]
# after-top: top + [min..max] observed after-top gaps
at_lo, at_hi = min(b_aftertop), max(b_aftertop)
w1 = (top25 + at_lo * DAY, top25 + at_hi * DAY)
# until-next-halving: H5 - [min..max] observed until-next gaps
un_lo, un_hi = min(b_until), max(b_until)
w2 = (H[5] - un_hi * DAY, H[5] - un_lo * DAY)
# after-halving: H4 + [min..max] observed after-halving gaps
ah_lo, ah_hi = min(b_after), max(b_after)
w3 = (H[4] + ah_lo * DAY, H[4] + ah_hi * DAY)
for name, w in [("after-top (364-406d)", w1), ("until-next-halving", w2), ("after-halving", w3)]:
    print(f"  {name:24} -> {w[0].date()} .. {w[1].date()}")
lo = max(w1[0], w2[0], w3[0]); hi = min(w1[1], w2[1], w3[1])
print(f"  OVERLAP of all three: {lo.date()} .. {hi.date()}  "
      f"({'they agree' if lo <= hi else 'NO overlap'})")

# ---- NULL: is the tightest bottom anchor real, or just how crashes play out? ----
print("\nNULL TEST — is the bottom's tightness real clock-lock, or process-intrinsic?")
print("  (block-bootstrap Bitcoin returns, same halving calendar, same mechanical turn rule,")
print("   measure how often a RANDOM path's bottoms cluster as tightly as observed)")
from empirical_null_test import extract_tops
df = pl_lib.load_prices()
c0 = df["c"].to_numpy(); dates = df.index
ret = np.diff(np.log(c0))
n = len(ret)
EPOCH = pl_lib.epoch_of(dates)
DSH = np.full(len(dates), np.nan)
for e, h in pl_lib.HALVINGS.items():
    m = dates >= h
    DSH[m] = (dates[m] - h).days
nxt = np.array([(next_halving(d) - d).days if next_halving(d) is not None else np.nan
                for d in dates])

def path_bottoms(c):
    tops = extract_tops(c)
    bots = []
    for k in range(len(tops) - 1):
        seg = c[tops[k]:tops[k + 1]]
        bots.append(tops[k] + int(np.argmin(seg)))
    return tops, bots

obs_aftertop = rng_days(b_aftertop)[0]
obs_until = rng_days(b_until)[0]
rngp = np.random.default_rng(11)
B, L = 2000, 90
hit_at, hit_un = 0, 0
for _ in range(B):
    nb = int(np.ceil(n / L))
    starts = rngp.integers(0, n, nb)
    idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
    cp = np.empty(n + 1); cp[0] = 1.0
    np.cumsum(ret[idx], out=cp[1:]); np.exp(cp[1:], out=cp[1:])
    tops, bots = path_bottoms(cp)
    if len(bots) < 3:
        continue
    # after-top gaps
    at = [int((dates.get_indexer([dates[b]])[0]) - t) for t, b in zip(tops[:-1], bots)]  # bar gap ~ days
    at = [bots[k] - tops[k] for k in range(len(bots))]
    # until-next-halving for each bottom (days)
    un = [nxt[b] for b in bots if not np.isnan(nxt[b])]
    if len(at) >= 3:
        best_at = min(max(s) - min(s) for s in [at[i:i+3] for i in range(len(at)-2)])
        hit_at += best_at <= obs_aftertop
    if len(un) >= 3:
        best_un = min(max(s) - min(s) for s in [un[i:i+3] for i in range(len(un)-2)])
        hit_un += best_un <= obs_until
print(f"  observed bottom range:  after-top {obs_aftertop}d   until-next-halving {obs_until}d")
print(f"  random path reproduces after-top  <= {obs_aftertop}d:  {hit_at/B*100:.0f}% of paths")
print(f"  random path reproduces until-next <= {obs_until}d:     {hit_un/B*100:.0f}% of paths")
