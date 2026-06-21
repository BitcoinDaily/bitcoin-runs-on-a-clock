"""
clock_explorations2.py — the next untested halving-clock ideas, each placebo-controlled.

  TEST 4  VOLATILITY CLOCK. The amplitude is dying, but does its TIMING lock? Align rolling
          realized volatility by days-since-halving across cycles. Does vol peak at a consistent
          phase? Correlate the vol-vs-phase curves; placebo = random-offset alignment.

  TEST 5  RETURN-BY-PHASE PROFILE. Pool every (days-since-halving, forward-90d-return) pair across
          cycles, average by phase bin. Is there a clean "boom zone" (positive) before the top and
          a "bust zone" (negative) after it? Where do the sign flips fall vs the 525-546d top
          window and the ~900d bottom?
"""
import numpy as np
import pandas as pd
import pl_lib

H = pl_lib.HALVINGS
df = pl_lib.load_prices()
c = df["c"]
ret = np.log(c).diff()
dsh = np.full(len(df), np.nan)
epoch = np.zeros(len(df), int)
for e, h in H.items():
    m = df.index >= h
    dsh[m] = (df.index[m] - h).days
    epoch[m] = e
df = df.assign(ret=ret, dsh=dsh, epoch=epoch)

pairs = [(1, 2), (1, 3), (2, 3)]

# ===================== TEST 4: volatility clock =====================
print("TEST 4 — VOLATILITY CLOCK (does vol PEAK at a consistent halving-day?)")
vol = df["ret"].rolling(30).std() * np.sqrt(365)
curves = {}
peak_phase = {}
for e in [1, 2, 3]:
    sub = vol[(df["epoch"] == e)]
    d = (sub.index - H[e]).days
    s = pd.Series(sub.values, index=d)
    s = s[(s.index >= 0) & (s.index < 1300) & s.notna()]
    s = s[~s.index.duplicated()]
    curves[e] = s.reindex(range(0, 1300)).interpolate()
    peak_phase[e] = int(curves[e].idxmax())
M = pd.DataFrame(curves).dropna()
cc = [M.corr().loc[a, b] for a, b in pairs]
print(f"  day-of-PEAK-vol after halving:  E1 {peak_phase[1]}d, E2 {peak_phase[2]}d, E3 {peak_phase[3]}d  "
      f"(range {max(peak_phase.values())-min(peak_phase.values())}d)")
print(f"  cross-cycle corr of the vol-vs-phase curve: {np.mean(cc):.2f}")
rngp = np.random.default_rng(5)
plac = []
for _ in range(500):
    sh = {e: curves[e].shift(int(rngp.integers(-365, 366))) for e in [1, 2, 3]}
    Mp = pd.DataFrame(sh).dropna()
    if len(Mp) > 200:
        plac.append(np.mean([Mp.corr().loc[a, b] for a, b in pairs]))
plac = np.array(plac)
print(f"  placebo (random-offset): mean {plac.mean():.2f}, P(random >= real) = {(plac>=np.mean(cc)).mean()*100:.1f}%\n")

# ===================== TEST 5: return-by-phase profile =====================
print("TEST 5 — RETURN-BY-PHASE (boom zone vs bust zone, pooled across cycles)")
fwd = c.shift(-90) / c - 1.0
d = df["dsh"].to_numpy()
f = fwd.to_numpy()
ok = (~np.isnan(d)) & (~np.isnan(f)) & (d < 1300)
d, f = d[ok], f[ok]
print(f"  {'phase (days after halving)':>28} {'avg fwd-90d return':>20} {'n':>6}")
bins = list(range(0, 1300, 130))
signs = []
for lo in bins:
    hi = lo + 130
    m = (d >= lo) & (d < hi)
    if m.sum() > 20:
        mr = f[m].mean()
        signs.append((lo, mr))
        bar = ("+" if mr > 0 else "-") * min(int(abs(mr) * 20) + 1, 30)
        print(f"  {f'{lo}-{hi}':>28} {mr*100:>+18.0f}% {m.sum():>6}  {bar}")
# where does it flip from boom to bust?
flip = None
for i in range(1, len(signs)):
    if signs[i-1][1] > 0 and signs[i][1] <= 0:
        flip = signs[i][0]; break
print(f"\n  boom->bust sign flip around day {flip} after halving  (top window = 525-546d)")
print(f"  (the bust zone is where the 'cash' timing rule sits out; the top window sits at the flip)")
