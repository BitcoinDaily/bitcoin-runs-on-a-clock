"""
clock_explorations.py — three new halving-clock tests, each built to be falsifiable.

  TEST 1  SEASONALITY OVERLAY. Align each cycle by days-since-halving, normalize, and ask:
          do the cycles trace the SAME shape (boom -> top -> bust -> recovery), not just two
          matching points? Quantify by cross-cycle correlation of the phase-aligned paths.

  TEST 2  PLACEBO ANCHORS (the key honesty test). The halving is one 4-year-ish clock. Compare
          the tops' cluster tightness under the HALVING vs (a) the US election cycle (also ~4yr),
          (b) a fixed 4-year calendar clock, (c) 2000 random 4-year clocks. If the halving is not
          meaningfully tighter than these, the "4-year cycle" is generic, not halving-specific.

  TEST 3  CROSS-ASSET. Ethereum has no halving. Do ETH's mechanical tops/bottoms still land at the
          same days-since-BTC-halving? If yes, the halving is a MARKET-WIDE clock, not just a
          BTC-supply effect.
"""
import numpy as np
import pandas as pd
import pl_lib
from empirical_null_test import extract_tops

H = pl_lib.HALVINGS
halv = [H[i] for i in sorted(H)]
DAY = pd.Timedelta(days=1)
BTC_TOPS = [pd.Timestamp(x) for x in ["2017-12-16", "2021-11-08", "2025-10-06"]]  # mature
ELECTIONS = [pd.Timestamp(x) for x in ["2012-11-06", "2016-11-08", "2020-11-03", "2024-11-05"]]


def rng(vals):
    return max(vals) - min(vals)


def days_after_nearest_prior(turns, anchors):
    out = []
    for t in turns:
        prior = [a for a in anchors if a <= t]
        if prior:
            out.append((t - max(prior)).days)
    return out


# ============================ TEST 1: seasonality overlay ============================
print("TEST 1 — SEASONALITY OVERLAY (do cycles trace the same shape in halving-time?)")
df = pl_lib.load_prices()
lp = np.log(df["c"])
curves = {}
for e in [1, 2, 3]:                       # full cycles
    h = H[e]; nxt = H[e + 1]
    sub = lp[(df.index >= h) & (df.index < nxt)]
    dsh = (sub.index - h).days
    s = pd.Series(sub.values - sub.values[0], index=dsh)        # normalize to halving-day = 0
    s = s[~s.index.duplicated()]
    curves[e] = s.reindex(range(0, 1300)).interpolate()
M = pd.DataFrame(curves).dropna()
corr = M.corr()
pairs = [(1, 2), (1, 3), (2, 3)]
cc = [corr.loc[a, b] for a, b in pairs]
print(f"  cross-cycle correlation of the halving-aligned price path: "
      f"E1-E2 {cc[0]:.2f}, E1-E3 {cc[1]:.2f}, E2-E3 {cc[2]:.2f}  (mean {np.mean(cc):.2f})")
# placebo: correlate cycles aligned by a RANDOM day offset instead of the halving
rngp = np.random.default_rng(3)
plac = []
for _ in range(500):
    shifted = {}
    for e in [1, 2, 3]:
        off = int(rngp.integers(-365, 366))
        shifted[e] = curves[e].shift(off)
    Mp = pd.DataFrame(shifted).dropna()
    if len(Mp) > 200:
        cp = Mp.corr()
        plac.append(np.mean([cp.loc[a, b] for a, b in pairs]))
plac = np.array(plac)
print(f"  placebo (random-offset alignment): mean corr {plac.mean():.2f}, "
      f"P(random >= halving alignment) = {(plac >= np.mean(cc)).mean()*100:.1f}%\n")

# ============================ TEST 2: placebo anchors ============================
print("TEST 2 — PLACEBO ANCHORS (is the tightness halving-specific or any 4-year clock?)")
r_halv = rng(days_after_nearest_prior(BTC_TOPS, halv))
r_elec = rng(days_after_nearest_prior(BTC_TOPS, ELECTIONS))
# fixed 4-year (1461d) calendar clock anchored at the first top
fixed = [BTC_TOPS[0] - 1461 * DAY, BTC_TOPS[0], BTC_TOPS[0] + 1461 * DAY, BTC_TOPS[0] + 2922 * DAY]
r_fixed = rng(days_after_nearest_prior(BTC_TOPS, fixed))
print(f"  tops' days-after-anchor RANGE:  halving {r_halv}d   election {r_elec}d   fixed-4yr {r_fixed}d")
# 2000 random 4-year clocks (fixed 1461d spacing, random phase)
rngp = np.random.default_rng(7)
ranges = []
for _ in range(2000):
    a0 = pd.Timestamp("2009-01-01") + int(rngp.integers(0, 1461)) * DAY
    anchors = [a0 + k * 1461 * DAY for k in range(0, 6)]
    da = days_after_nearest_prior(BTC_TOPS, anchors)
    if len(da) == 3:
        ranges.append(rng(da))
ranges = np.array(ranges)
print(f"  random 4-year clocks: median range {np.median(ranges):.0f}d, "
      f"P(random clock <= halving's {r_halv}d) = {(ranges <= r_halv).mean()*100:.1f}%")
print(f"  -> the halving anchor is tighter than {100-(ranges<=r_halv).mean()*100:.0f}% of random 4-year clocks\n")

# ============================ TEST 3: cross-asset ============================
print("TEST 3 — CROSS-ASSET (does ETH align to the BTC halving clock?)")
try:
    eth = pd.read_csv("eth_daily.csv", parse_dates=["date"]).set_index("date")["close"]
    ec = eth.to_numpy()
    etops = extract_tops(ec)
    edates = eth.index
    def dsh_of(d):
        prior = [h for h in halv if h <= d]
        return (d - max(prior)).days if prior else None
    print("  ETH mechanical tops and their days-since-BTC-halving:")
    for i in etops:
        d = edates[i]
        print(f"    {d.date()}  ${ec[i]:>7,.0f}   {dsh_of(d)} days after BTC halving")
    mature = [dsh_of(edates[i]) for i in etops if dsh_of(edates[i]) and dsh_of(edates[i]) > 400]
    if len(mature) >= 2:
        print(f"  ETH mature-top days-after-halving: {mature}  (BTC tops: 525/546/534)")
except Exception as e:
    print("  ETH test failed:", type(e).__name__, str(e)[:100])
