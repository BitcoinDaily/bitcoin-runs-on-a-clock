"""block_phase_tests.py — the rest of the day-phase battery, re-run in BLOCK phase.

  TEST 3  PLACEBO CLOCKS in block space. Day-clock (clock_explorations.py TEST 2) found the
          halving beats the election clock (21d vs 68d) and 100% of random 4-year PHASES. In
          block space the halving clock is EXACTLY periodic (210,000 blocks by protocol), so the
          informative placebo flips: random OFFSET is near-degenerate (period does the work), and
          the real test is whether the 210k PERIOD is special vs random periods.
  TEST 4  SEASONALITY OVERLAY. Day-clock: cycles trace the same shape aligned by days-since-halving
          (mean cross-cycle corr 0.72, placebo 0.02, P=2.8%). Does aligning by BLOCKS-since-halving
          (which rescales each cycle by its own chain speed) trace a MORE similar shape?
  TEST 5  RETURN-BY-PHASE. Day-clock: fwd-90d returns positive 0-520d, negative 520-910d, positive
          recovery. Where do the sign flips sit in BLOCKS, and are the bins cleaner or muddier?
  TEST 6a E1 CHAIN-SPEED RECONCILIATION. Quantify how much of the 2013 top's day-earliness
          (ratio 0.686 of the mature mean) is the fast early chain (block ratio 0.791). (The
          hostile 4-top NULL for E1 lives in block_phase_null.py.)
  TEST 7  VOL CLOCK — the honest day miss (P=0.19). Re-check in block phase; a miss stays a miss.

Same placebo seeds as the day-clock scripts (seasonality 3, placebo-clocks 7, vol 5). n=3/4 turns
throughout; descriptive, no HAC/parametric significance claims.
"""
import numpy as np
import pandas as pd
import pl_lib
from empirical_null_test import extract_tops
from block_phase_null import load_aligned, epoch_max_tops, HALVING_HEIGHT

H = pl_lib.HALVINGS
PAIRS = [(1, 2), (1, 3), (2, 3)]

# height series (untruncated) for mapping arbitrary anchor dates -> block heights
HEIGHT = pd.read_csv("block_height_daily.csv", parse_dates=["date"]).set_index("date")["height_eod"]


def height_asof(date):
    """Block height at/just before a calendar date (exogenous clock lookup)."""
    return int(HEIGHT.asof(pd.Timestamp(date)))


def rng_(v):
    return max(v) - min(v)


def blocks_after_prior(top_h, anchor_hs):
    """For each top height, blocks since the nearest prior anchor height."""
    out = []
    for h in top_h:
        prior = [a for a in anchor_hs if a <= h]
        if prior:
            out.append(h - max(prior))
    return out


def main():
    c, dates, epoch, dah, bah = load_aligned()
    lp = np.log(c)
    tops = extract_tops(c)
    em = epoch_max_tops(tops, c, epoch)
    top_idx = {e: i for e, i in em}
    mature_tops = [top_idx[e] for e in (2, 3, 4)]
    top_h = [int(bah[i] + HALVING_HEIGHT[epoch[i]]) for i in mature_tops]     # absolute heights
    top_dates = [dates[i] for i in mature_tops]
    print(f"mature tops (E2/E3/E4): heights {top_h}  dates {[str(d.date()) for d in top_dates]}")

    # ================= TEST 3: placebo clocks in block space =================
    print("\nTEST 3 — PLACEBO CLOCKS IN BLOCK SPACE")
    halv_range = rng_([h % 210000 for h in top_h])   # offset-0 210k clock == the halving
    elec_dates = ["2012-11-06", "2016-11-08", "2020-11-03", "2024-11-05"]
    elec_h = [height_asof(d) for d in elec_dates]
    elec_range = rng_(blocks_after_prior(top_h, elec_h))
    # fixed 4-year CALENDAR clock (day-clock's anchor), mapped through the height series
    t0 = pd.Timestamp("2017-12-16")
    fixed_dates = [t0 - pd.Timedelta(days=1461), t0, t0 + pd.Timedelta(days=1461), t0 + pd.Timedelta(days=2922)]
    fixed_h = [height_asof(d) for d in fixed_dates]
    fixed_range = rng_(blocks_after_prior(top_h, fixed_h))
    print(f"  halving-block clock (period 210,000, offset 0):  top range {halv_range:>6,} blocks")
    print(f"  election-dates mapped to heights:                top range {elec_range:>6,} blocks")
    print(f"  fixed-4yr-calendar mapped to heights:            top range {fixed_range:>6,} blocks")

    rng = np.random.default_rng(7)
    # (a) fixed-210k period, RANDOM OFFSET — expected near-degenerate (period, not phase)
    off_ranges = []
    for _ in range(2000):
        o = int(rng.integers(0, 210000))
        off_ranges.append(rng_([(h - o) % 210000 for h in top_h]))
    off_ranges = np.array(off_ranges)
    p_off = (off_ranges <= halv_range).mean() * 100
    # (b) RANDOM PERIOD block clock — is 210k special?
    per_ranges = []
    for _ in range(2000):
        P = int(rng.integers(100000, 320001))
        o = int(rng.integers(0, P))
        per_ranges.append(rng_([(h - o) % P for h in top_h]))
    per_ranges = np.array(per_ranges)
    p_per = (per_ranges <= halv_range).mean() * 100
    print(f"  fixed-210k, RANDOM OFFSET (2000): median range {np.median(off_ranges):>6,.0f}, "
          f"P(<= halving {halv_range:,}) = {p_off:.1f}%   <- period does the work, not phase")
    print(f"  RANDOM PERIOD (2000):             median range {np.median(per_ranges):>6,.0f}, "
          f"P(<= halving {halv_range:,}) = {p_per:.1f}%   <- is the 210k PERIOD special?")
    print(f"  DAY reference: halving 21d, election 68d, fixed-4yr 1423d, random-4yr-PHASE P(<=21)=0%")

    # ================= TEST 4: seasonality overlay, block vs day =================
    print("\nTEST 4 — SEASONALITY OVERLAY (block alignment vs day alignment)")

    def overlay(unit):
        curves = {}
        for e in (1, 2, 3):
            m = (epoch == e) & (dates < H[e + 1])
            y = lp[m]
            if unit == "day":
                x = dah[m]
                grid = np.arange(0, 1300)
            else:
                x = bah[m]
                grid = np.arange(0, 190000, 500)
            s = pd.Series(y, index=x)
            s = s[~s.index.duplicated()].sort_index()
            s = s - s.iloc[0]                                   # normalize halving-phase = 0
            curves[e] = s.reindex(s.index.union(grid)).interpolate().reindex(grid)
        M = pd.DataFrame(curves).dropna()
        cc = [M.corr().loc[a, b] for a, b in PAIRS]
        return np.mean(cc), cc, curves, grid

    day_mean, day_cc, _, _ = overlay("day")
    blk_mean, blk_cc, blk_curves, blk_grid = overlay("block")
    print(f"  DAY  aligned: E1-E2 {day_cc[0]:.2f} E1-E3 {day_cc[1]:.2f} E2-E3 {day_cc[2]:.2f}  mean {day_mean:.2f}")
    print(f"  BLOCK aligned: E1-E2 {blk_cc[0]:.2f} E1-E3 {blk_cc[1]:.2f} E2-E3 {blk_cc[2]:.2f}  mean {blk_mean:.2f}")
    # placebo for the block overlay: random block-offset (seed 3, matching day script), ~28% window
    rngp = np.random.default_rng(3)
    plac = []
    for _ in range(500):
        sh = {e: blk_curves[e].reindex(blk_grid).interpolate().shift(int(rngp.integers(-108, 109)))
              for e in (1, 2, 3)}          # +/-108 grid steps = +/-54000 blocks ~= day's +/-365d
        Mp = pd.DataFrame(sh).dropna()
        if len(Mp) > 150:
            plac.append(np.mean([Mp.corr().loc[a, b] for a, b in PAIRS]))
    plac = np.array(plac)
    print(f"  BLOCK placebo (random-offset): mean {plac.mean():.2f}, P(random >= block-aligned) = "
          f"{(plac >= blk_mean).mean()*100:.1f}%   (DAY was 0.72 / 0.02 / P=2.8%)")
    print(f"  -> block alignment {'BEATS' if blk_mean > day_mean else 'does NOT beat'} day alignment "
          f"({blk_mean:.2f} vs {day_mean:.2f})")

    # ================= TEST 5: return-by-phase, block vs day =================
    print("\nTEST 5 — RETURN-BY-PHASE (fwd-90d return by block phase vs day phase)")
    fwd = np.concatenate([c[90:] / c[:-90] - 1.0, np.full(90, np.nan)])
    for unit, ph, width, top in (("DAY", dah, 130, 1300), ("BLOCK", bah, 19000, 190000)):
        print(f"  {unit} phase bins:")
        signs = []
        for lo in range(0, top, width):
            m = (ph >= lo) & (ph < lo + width) & ~np.isnan(fwd)
            if m.sum() > 20:
                mr = np.nanmean(fwd[m])
                signs.append((lo, mr))
                bar = ("+" if mr > 0 else "-") * min(int(abs(mr) * 20) + 1, 24)
                unit_lbl = f"{lo}-{lo+width}"
                print(f"    {unit_lbl:>16} {mr*100:>+6.0f}%  n={m.sum():>4}  {bar}")
        flip = next((signs[i][0] for i in range(1, len(signs))
                     if signs[i-1][1] > 0 and signs[i][1] <= 0), None)
        print(f"    boom->bust flip at phase ~{flip} ({unit})")

    # ================= TEST 6a: E1 chain-speed reconciliation =================
    print("\nTEST 6a — E1 (2013 TOP) CHAIN-SPEED RECONCILIATION")
    e1 = top_idx.get(1)
    e1_day, e1_blk = dah[e1], bah[e1]
    mat_day_mean = np.mean([dah[top_idx[e]] for e in (2, 3, 4)])
    mat_blk_mean = np.mean([bah[top_idx[e]] for e in (2, 3, 4)])
    r_day, r_blk = e1_day / mat_day_mean, e1_blk / mat_blk_mean
    e1_speed = e1_blk / e1_day
    mat_speed = mat_blk_mean / mat_day_mean
    ctf_day = e1_blk / mat_speed                        # counterfactual day if E1 ran at mature speed
    print(f"  2013 top: day {e1_day:.0f} (ratio {r_day:.3f} of mature mean {mat_day_mean:.0f}d), "
          f"block {e1_blk:.0f} (ratio {r_blk:.3f} of mature mean {mat_blk_mean:.0f})")
    print(f"  early-chain speed {e1_speed:.1f} blk/day vs mature {mat_speed:.1f} blk/day (+{(e1_speed/mat_speed-1)*100:.0f}%)")
    frac = (r_blk - r_day) / (1 - r_day) * 100
    print(f"  earliness gap closed by block coordinate: {frac:.0f}%  (day gap {1-r_day:.3f} -> block gap {1-r_blk:.3f})")
    print(f"  counterfactual: at mature speed the 2013 top's {e1_blk:.0f} blocks = day {ctf_day:.0f} "
          f"(vs actual {e1_day:.0f}); ~{(ctf_day-e1_day)/(mat_day_mean-e1_day)*100:.0f}% of the way to the mature mean")

    # ================= TEST 7: vol clock, block vs day =================
    print("\nTEST 7 — VOLATILITY CLOCK (the day miss P=0.19; re-check in block phase)")
    ret = pd.Series(np.concatenate([[np.nan], np.diff(lp)]), index=range(len(c)))
    vol = ret.rolling(30).std().to_numpy() * np.sqrt(365)
    for unit, ph, grid, seedv, day_ref in (
            ("DAY", dah, np.arange(0, 1300), 5, None),
            ("BLOCK", bah, np.arange(0, 190000, 500), 5, None)):
        curves, peak = {}, {}
        for e in (1, 2, 3):
            m = (epoch == e) & ~np.isnan(vol) & ~np.isnan(ph)
            s = pd.Series(vol[m], index=ph[m])
            s = s[(s.index >= 0) & (s.index < grid[-1])]
            s = s[~s.index.duplicated()].sort_index()
            curves[e] = s.reindex(s.index.union(grid)).interpolate().reindex(grid)
            peak[e] = int(grid[np.nanargmax(curves[e].to_numpy())])
        M = pd.DataFrame(curves).dropna()
        cc = np.mean([M.corr().loc[a, b] for a, b in PAIRS])
        rngv = np.random.default_rng(seedv)
        span = 365 if unit == "DAY" else 52000
        plac = []
        for _ in range(500):
            sh = {e: curves[e].shift(int(rngv.integers(-span, span + 1)) if unit == "DAY"
                                     else int(rngv.integers(-104, 105))) for e in (1, 2, 3)}
            Mp = pd.DataFrame(sh).dropna()
            if len(Mp) > 150:
                plac.append(np.mean([Mp.corr().loc[a, b] for a, b in PAIRS]))
        plac = np.array(plac)
        pk = list(peak.values())
        print(f"  {unit}: peak-vol phase E1 {pk[0]} E2 {pk[1]} E3 {pk[2]} (range {max(pk)-min(pk):,}), "
              f"cross-cycle corr {cc:.2f}, placebo P(random>=real) {(plac>=cc).mean()*100:.1f}%")
    print("  (day clock was a MISS at P=19.4%; report block honestly, hit or miss)")


if __name__ == "__main__":
    main()
