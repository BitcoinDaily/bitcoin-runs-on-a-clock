"""
satoshi_clock.py — (1) the permutation/null test for the clock's 6 calls (3 tops + 3 bottoms),
(2) the SATOSHI CLOCK indicator: Bitcoin's state in two time-anchored coordinates.

THE 6 CALLS (mechanical turns from cycle_callers.py, Coin Metrics data):
  TOPS, days after their halving (mature cycles; E1's 371d is the documented warmup exception):
      2017-12-16 -> 525    2021-11-08 -> 546    2025-10-06 -> 534      spread = 21d
  BOTTOMS, days after their cycle top (all three completed bears, incl. E1's):
      2015-01-14 -> 406    2018-12-15 -> 364    2022-11-09 -> 366      spread = 42d

NULL HYPOTHESIS: turn timing carries no information — each top lands uniformly at random in a
plausible after-halving window, each bottom uniformly in a plausible after-top window. The test
statistic is the observed RANGE (max-min), stated before testing. Exact formula for n uniform
points in [0,W]:  P(range <= r) = n(r/W)^(n-1) - (n-1)(r/W)^n.  Monte Carlo cross-check.
Window choice is the only lever, so we report a CONSERVATIVE-to-GENEROUS grid and let every
cell be seen.

THE SATOSHI CLOCK ("the amount cut in half every 4 years" — Satoshi, 2009-01-08):
Bitcoin's market state described by two time-anchored coordinates:
  CLOCK  = days since the last halving (the angle: where in the 4-year revolution)
  SPRING = causal power-law deviation z (the radius: how stretched from the time-trend)
Tops have occurred at CLOCK 525-546 with SPRING high; bottoms at 364-406 days after the top
(equivalently CLOCK ~889-924) with SPRING low. Plotting SPRING against CLOCK across epochs
traces a damped spiral: the radius shrinks every cycle (dying amplitude = why every price
threshold fails) while the angle of the turns stays fixed (the clock).
"""
import numpy as np
import pandas as pd
import pl_lib

TOPS_AH = np.array([525, 546, 534])     # days after halving
BOTS_AT = np.array([406, 364, 366])     # days after their top
HALVING_4 = pd.Timestamp("2024-04-20")
TOP_4 = pd.Timestamp("2025-10-06")


def p_range_uniform(r, W, n):
    """P(range of n iid U[0,W] points <= r), exact."""
    x = r / W
    return n * x ** (n - 1) - (n - 1) * x ** n


def mc_range(r, W, n, B=2_000_000, seed=11):
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, W, size=(B, n))
    return float(((u.max(1) - u.min(1)) <= r).mean())


def main():
    print("=== 1. PERMUTATION / NULL TEST — could the 6 calls be luck? ===")
    r_top = TOPS_AH.max() - TOPS_AH.min()
    r_bot = BOTS_AT.max() - BOTS_AT.min()
    print(f"  observed: top range {r_top}d (525/546/534), bottom range {r_bot}d (406/364/366)\n")
    print(f"  {'top window W':>14} {'P(top)':>10} | {'bot window W':>14} {'P(bot)':>10} | "
          f"{'joint p':>10}")
    grid = [(1458, 800), (1100, 700), (900, 600), (700, 500)]
    for Wt, Wb in grid:
        pt = p_range_uniform(r_top, Wt, 3)
        pb = p_range_uniform(r_bot, Wb, 3)
        print(f"  {Wt:>14} {pt:>10.5f} | {Wb:>14} {pb:>10.5f} | {pt*pb:>10.2e}")
    # Monte Carlo cross-check on the most conservative cell
    pt_mc = mc_range(r_top, 700, 3)
    pb_mc = mc_range(r_bot, 500, 3)
    print(f"  MC cross-check (W=700/500): P(top)={pt_mc:.5f} P(bot)={pb_mc:.5f} "
          f"joint={pt_mc*pb_mc:.2e}")
    print("  Even with the MOST conservative windows (turns forced into narrow plausible bands),"
          "\n  the joint probability of both clusters arising by chance is ~1e-4 or smaller.")
    # as fraction of (varying) halving gap
    gaps = [1402, 1440, 1458]
    fr = [t / g for t, g in zip(TOPS_AH, gaps)]
    print(f"  footnote: tops as FRACTION of their (varying) halving gap: "
          f"{', '.join(f'{f:.3f}' for f in fr)} — also tight.\n")

    print("=== 2. THE SATOSHI CLOCK — current reading ===")
    df = pl_lib.build_signals(pl_lib.load_close_csv("btc_daily.csv"))
    now = df.index[-1]
    clock = (now - HALVING_4).days
    since_top = (now - TOP_4).days
    z = df["pl_z"].iloc[-1]
    px = df["c"].iloc[-1]
    print(f"  as of {now.date()}  (BTC ${px:,.0f})")
    print(f"  CLOCK  = {clock}d after the 2024-04-20 halving")
    print(f"  SPRING = {z:+.2f} (causal power-law deviation z)")
    print(f"  state: post-top bear, {since_top}d after the 2025-10-06 top")
    b1 = TOP_4 + pd.Timedelta(days=int(BOTS_AT.min()))
    b2 = TOP_4 + pd.Timedelta(days=int(BOTS_AT.max()))
    print(f"  BOTTOM WINDOW (top + 364..406d): {b1.date()} .. {b2.date()}")
    h1 = HALVING_4 + pd.Timedelta(days=889)
    h2 = HALVING_4 + pd.Timedelta(days=924)
    print(f"    cross-check via after-halving anchor (889-924d): {h1.date()} .. {h2.date()}")
    nh = pd.Timestamp("2028-04-15")     # ~210,000 blocks after 2024-04-20 at ~10min/block
    t1 = nh + pd.Timedelta(days=int(TOPS_AH.min()))
    t2 = nh + pd.Timedelta(days=int(TOPS_AH.max()))
    print(f"  NEXT TOP WINDOW (next halving ~{nh.date()} + 525..546d): "
          f"{t1.date()} .. {t2.date()}")

    print("\n=== 3. damped-spiral table: SPRING at each cycle's turns (the dying amplitude) ===")
    turns = [("TOP", "2013-12-04"), ("BOT", "2015-01-14"), ("TOP", "2017-12-16"),
             ("BOT", "2018-12-15"), ("TOP", "2021-11-08"), ("BOT", "2022-11-09"),
             ("TOP", "2025-10-06"), ("now", str(now.date()))]
    for kind, d in turns:
        t = pd.Timestamp(d)
        if t in df.index:
            row = df.loc[t]
        else:
            row = df.iloc[df.index.get_indexer([t], method="nearest")[0]]
        hs = [h for h in pl_lib.HALVINGS.values() if h <= t]
        ph = (t - max(hs)).days if hs else -1
        print(f"  {kind:4} {d}  CLOCK={ph:>4}d  SPRING={row['pl_z']:+.2f}")


if __name__ == "__main__":
    main()
