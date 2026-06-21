"""
clock_timing_adversarial.py — red-team the clock-timing backtest.
Is "timing beats hold 53x, 4/4 cycles" real halving-clock skill, or just generic
drawdown/vol-drag avoidance with hindsight-placed windows? Three tests:

  A. WINDOW-PLACEMENT SWEEP. Slide a fixed-width (~375d) cash window's START across the
     whole cycle (0..1080d after halving). Real timing => ratio peaks sharply at the true
     top->bottom window and LOSES (ratio<1) on the boom. Vol-drag artifact => most placements
     still beat hold.
  B. PLACEBO vs RANDOM CASH. Compare the real window to (i) the mirror boom window, and
     (ii) the average of 500 RANDOM 30%-of-days cash masks (same time-out, no clock logic).
  C. LEAVE-ONE-CYCLE-OUT. Pick the sell/buy days that maximize the stacked ratio on the OTHER
     three cycles, then apply to the held-out cycle. Honest out-of-sample: does the held-out
     cycle still beat hold, and by how much vs the in-sample-optimal?
"""
import numpy as np
import pandas as pd
import pl_lib
from clock_timing_backtest import run, per_cycle, stacked, days_since_halving

df_raw = pl_lib.load_prices()
DSH = days_since_halving(df_raw.index)
RET = df_raw["c"].pct_change().fillna(0.0).to_numpy()
EPOCH = pl_lib.epoch_of(df_raw.index)
WIDTH = 900 - 525  # 375 days


def stacked_ratio_wins(sell, buy):
    d = run(df_raw, sell, buy)
    pc = per_cycle(d); st = stacked(d)
    wins = int((pc["st_ret"] > pc["bh_ret"]).sum())
    return st["ratio"], wins, st["st_dd"]


print("A. WINDOW-PLACEMENT SWEEP  (fixed width 375d, slide the cash window's start)")
print(f"   {'start':>6} {'window':>12} {'ratio':>8} {'wins':>5}   (ratio<1 = LOSES to hold)")
peak = (0, -1)
for start in range(0, 1081, 60):
    sell, buy = start, start + WIDTH
    r, w, _ = stacked_ratio_wins(sell, buy)
    if r > peak[1]:
        peak = (start, r)
    flag = "  <-- TRUE bust window" if start in (480, 540) else ("  (boom)" if start < 400 else "")
    print(f"   {start:>6} {f'{sell}-{buy}':>12} {r:>7.1f}x {w:>5}{flag}")
print(f"   peak ratio at start={peak[0]}d ({peak[1]:.0f}x)\n")

print("B. PLACEBO vs RANDOM CASH")
r_real, w_real, dd_real = stacked_ratio_wins(525, 900)
r_boom, w_boom, _ = stacked_ratio_wins(150, 150 + WIDTH)   # cash during the run-up instead
print(f"   real bust window (525-900): {r_real:5.1f}x, wins {w_real}/4")
print(f"   placebo boom window (150-525): {r_boom:5.1f}x, wins {w_boom}/4")
rng = np.random.default_rng(0)
n_days = len(RET)
frac_cash = float(((DSH >= 525) & (DSH <= 900)).mean())  # match the real time-out
ratios = []
for _ in range(500):
    mask = rng.random(n_days) < frac_cash               # random ~30% cash, no clock logic
    pos = pd.Series(np.where(mask, 0.0, 1.0), index=df_raw.index).shift(1).fillna(1.0).to_numpy()
    st_eq = np.cumprod(1 + pos * RET); bh_eq = np.cumprod(1 + RET)
    ratios.append(st_eq[-1] / bh_eq[-1])
ratios = np.array(ratios)
print(f"   random {frac_cash*100:.0f}%-cash (500 draws): median {np.median(ratios):.2f}x, "
      f"p95 {np.percentile(ratios,95):.2f}x, P(ratio>=1) = {(ratios>=1).mean()*100:.0f}%, "
      f"P(ratio>={r_real:.0f}) = {(ratios>=r_real).mean()*100:.1f}%\n")

print("C. LEAVE-ONE-CYCLE-OUT  (window optimized on the OTHER 3 cycles, applied out-of-sample)")
def stacked_ratio_on_epochs(sell, buy, epochs):
    pos = np.where(np.isnan(DSH), 1.0, np.where((DSH >= sell) & (DSH <= buy), 0.0, 1.0))
    pos = pd.Series(pos, index=df_raw.index).shift(1).fillna(1.0).to_numpy()
    m = np.isin(EPOCH, epochs)
    st = np.cumprod(1 + pos[m] * RET[m]); bh = np.cumprod(1 + RET[m])
    return st[-1] / bh[-1], st[-1] - 1, bh[-1] - 1
grid = [(s, b) for s in range(490, 561, 10) for b in range(840, 941, 20)]
print(f"   {'held-out':>9} {'best window on other 3':>24} {'OOS ratio':>10} {'OOS timing%':>12} {'OOS hold%':>10}")
for held in [1, 2, 3, 4]:
    others = [e for e in [1, 2, 3, 4] if e != held]
    best = max(grid, key=lambda sb: stacked_ratio_on_epochs(sb[0], sb[1], others)[0])
    r_oos, st_oos, bh_oos = stacked_ratio_on_epochs(best[0], best[1], [held])
    verdict = "WIN" if r_oos > 1 else "LOSE"
    print(f"   {EPOCH_NAME if False else held:>9} {f'sell {best[0]}, buy {best[1]}':>24} "
          f"{r_oos:>9.1f}x {st_oos*100:>+11,.0f}% {bh_oos*100:>+9,.0f}%  {verdict}")
