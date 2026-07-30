"""block_phase_null.py — THE SPINE, re-run in BLOCK phase.

The paper's decisive turn-timing test (empirical_null_test.py) asks: could a Bitcoin-like
drawdown process with NO relationship to the halving schedule reproduce a turn regularity as
tight as history's? It scores mechanical tops/bottoms of block-bootstrap synthetic price paths
in DAYS-after-halving. Here we re-score the IDENTICAL machinery (same SEED=31, same B=2000, same
block lengths L, same extract_tops rule) in BLOCKS-after-halving, using the exogenous real
date->height series (block_height_daily.csv). The height mapping is independent of price, so
scoring a price-null through it is clean.

Design choice that removes a confound: each synthetic path is scored in BOTH coordinates in the
SAME pass over the SAME random draws, so any day-vs-block difference is the coordinate change, not
different randomness. The real series is scored first as a self-check and to fix the observed
thresholds mechanically (no hand-entered numbers).

Observed headline (mempool noon lookups, block_clock_data.json):
  TOP mature range  21 days  <->  1,695 blocks
  BOTTOM after-own-halving range  135 days  <->  5,024 blocks   (block = anchor-free: after-own
      and to-next are complementary, sum to exactly 210,000, so both give the SAME range)

n=3 mature epochs. Descriptive; the p is a null-reproduction fraction, no HAC/parametric claim.
"""
import numpy as np
import pandas as pd
import pl_lib
from empirical_null_test import extract_tops, DD, DD_OPEN, B, LS, SEED, TOP_RANGE_OBS, BOT_RANGE_OBS

HEIGHT_CSV = "block_height_daily.csv"
HALVING_HEIGHT = {1: 210000, 2: 420000, 3: 630000, 4: 840000}
MATURE_TOP_EPOCHS = (2, 3, 4)
MATURE_BOT_EPOCHS = (1, 2, 3)


def load_aligned():
    """Price series truncated to the common span with the height series; returns arrays aligned
    by calendar position: close c, dates, epoch, days-after-halving dah, blocks-after-halving bah."""
    df = pl_lib.load_prices()
    h = pd.read_csv(HEIGHT_CSV, parse_dates=["date"]).set_index("date")["height_eod"]
    df = df.join(h.rename("height"), how="left")
    last = df["height"].last_valid_index()
    df = df.loc[:last]                       # truncate tail to where height exists (2026-05-23)
    c = df["c"].to_numpy()
    dates = df.index
    epoch = pl_lib.epoch_of(dates)
    height = df["height"].to_numpy()
    dah = np.full(len(df), np.nan)
    bah = np.full(len(df), np.nan)
    for e, hd in pl_lib.HALVINGS.items():
        m = np.asarray(dates >= hd)
        dah[m] = (dates[m] - hd).days
        bah[m] = height[m] - HALVING_HEIGHT[e]   # blocks after that epoch's halving
    return c, dates, epoch, dah, bah


def segment_bottoms(c, tops):
    """Between each consecutive top pair, the min-price index = a bottom. Returns indices.
    Used ONLY for the empirical_null continuity stat (top->bottom gap best-3)."""
    bots = []
    for k in range(len(tops) - 1):
        seg = c[tops[k]:tops[k + 1]]
        bots.append(tops[k] + int(np.argmin(seg)))
    return np.array(bots, int)


def epoch_max_tops(tops, c, epoch):
    """One top per epoch = the highest-price qualifying top in that epoch (the cycle top).
    Returns a list of (epoch, idx) sorted by idx."""
    by_ep = {}
    for i in tops:
        e = epoch[i]
        if e not in by_ep or c[i] > c[by_ep[e]]:
            by_ep[e] = i
    return sorted(((e, by_ep[e]) for e in by_ep), key=lambda t: t[1])


def cycle_bottoms(c, tops, epoch):
    """The cycle low BELONGING to each cycle = the min-price trough between consecutive
    epoch-max tops, labeled by the epoch of the EARLIER top (the cycle it closes out). This is
    the construction that reproduces the observed 2015-01-14 / 2018-12-15 / 2022-11-xx lows; it
    is robust to double-tops (Apr+Nov 2021) that a naive lowest-close-per-epoch rule mishandles
    because of Bitcoin's secular uptrend. Returns {cycle_label: trough_idx}."""
    em = epoch_max_tops(tops, c, epoch)
    out = {}
    for (ea, ia), (eb, ib) in zip(em[:-1], em[1:]):
        if ib > ia + 1:
            trough = ia + int(np.argmin(c[ia:ib]))
            out[ea] = trough          # cycle ea's bottom = trough after its top
    return out


def cycle_bottom_range(c, tops, epoch, phase, want=MATURE_BOT_EPOCHS):
    """Range of `phase` across the cycle bottoms of the wanted cycles; inf if any is missing."""
    cb = cycle_bottoms(c, tops, epoch)
    if not all(e in cb for e in want):
        return np.inf
    ph = [phase[cb[e]] for e in want]
    if any(np.isnan(p) for p in ph):
        return np.inf
    return max(ph) - min(ph)


def top_phase_range(tops, phase, epoch, epochs=MATURE_TOP_EPOCHS):
    """Tops: (A) selection-min range and (B) epoch-max deterministic range, in `phase` units.
    Epoch-max = last qualifying top per epoch (== highest price, since every top is an ATH).
    `epochs` selects the epoch set: (2,3,4)=clean mature; (1,2,3,4)=hostile, forcing in the
    early-era 2013 top the paper excludes."""
    by_ep = {e: [phase[i] for i in tops if epoch[i] == e] for e in epochs}
    if not all(by_ep[e] for e in epochs):
        return np.inf, np.inf, sum(len(v) for v in by_ep.values())
    from itertools import product
    sel_min = np.inf
    for combo in product(*[by_ep[e] for e in epochs]):
        sel_min = min(sel_min, max(combo) - min(combo))
    sel_epochmax = [by_ep[e][-1] for e in epochs]
    epochmax_range = max(sel_epochmax) - min(sel_epochmax)
    return epochmax_range, sel_min, sum(len(v) for v in by_ep.values())


def score(c, dates, epoch, dah, bah):
    """Full turn scoring in both coordinates. Returns a dict of range statistics."""
    tops = extract_tops(c)
    out = {}
    # ---- tops: clean mature (E2/E3/E4) ----
    out["top_em_day"], out["top_sel_day"], out["n_mat_top"] = top_phase_range(tops, dah, epoch)
    out["top_em_blk"], out["top_sel_blk"], _ = top_phase_range(tops, bah, epoch)
    # ---- tops: HOSTILE 4-top (force in the early-era 2013 top, E1/E2/E3/E4) ----
    out["top_h4_day"], _, _ = top_phase_range(tops, dah, epoch, epochs=(1, 2, 3, 4))
    out["top_h4_blk"], _, _ = top_phase_range(tops, bah, epoch, epochs=(1, 2, 3, 4))
    # ---- cycle bottoms: after-own-halving range (the rescue statistic) ----
    out["bot_det_day"] = cycle_bottom_range(c, tops, epoch, dah)
    out["bot_det_blk"] = cycle_bottom_range(c, tops, epoch, bah)
    # ---- continuity: empirical_null's top->bottom GAP best-3-subset range (days) ----
    bots = segment_bottoms(c, tops)
    gaps = [(dates[b] - dates[t]).days for t, b in zip(tops[:-1], bots)]
    gap_r = np.inf
    if len(gaps) >= 3:
        g = np.sort(np.array(gaps, float))
        gap_r = float(np.min(g[2:] - g[:-2]))
    out["bot_gap_day"] = gap_r
    # ---- adversarial: is the bottom rarity INDEPENDENT of the tops, or inherited? ----
    # top->cycle-bottom LAG range across the 3 mature cycles, in day and block phase. This is the
    # part of the bottom NOT explained by its own top's phase. If it clusters as loosely as the
    # paper's gap stat, the after-halving bottom rarity is largely the top phase-lock propagated.
    em = epoch_max_tops(tops, c, epoch)
    top_of = {e: i for e, i in em}
    cb = cycle_bottoms(c, tops, epoch)
    out["bot_valid"] = int(all(e in cb for e in MATURE_BOT_EPOCHS))
    for unit, ph in (("day", dah), ("blk", bah)):
        lag_r = np.inf
        if out["bot_valid"] and all(e in top_of for e in MATURE_BOT_EPOCHS):
            lags = [ph[cb[e]] - ph[top_of[e]] for e in MATURE_BOT_EPOCHS]
            if not any(np.isnan(v) for v in lags):
                lag_r = max(lags) - min(lags)
        out[f"bot_lag_{unit}"] = lag_r
    return out


def main():
    c, dates, epoch, dah, bah = load_aligned()
    print(f"aligned span {dates[0].date()} -> {dates[-1].date()}  ({len(dates)} rows; "
          f"tail truncated to height coverage)")

    # ---------- observed (mechanical, from the real series) ----------
    o = score(c, dates, epoch, dah, bah)
    tops = extract_tops(c)
    em = epoch_max_tops(tops, c, epoch)
    cb = cycle_bottoms(c, tops, epoch)
    print("\nreal-series mechanical EPOCH-MAX TOPS (epoch : date : day-after-halving : block-after-halving):")
    for e, i in em:
        tag = "MATURE" if e in MATURE_TOP_EPOCHS else "early"
        print(f"  ep{e} {dates[i].date()}  day {dah[i]:>5.0f}  blk {bah[i]:>8.0f}  ${c[i]:>9,.0f}  {tag}")
    print("real-series mechanical CYCLE BOTTOMS (trough between consecutive epoch-max tops):")
    for e in sorted(cb):
        i = cb[e]
        tag = "MATURE" if e in MATURE_BOT_EPOCHS else "early"
        print(f"  cycle{e} {dates[i].date()}  day {dah[i]:>5.0f}  blk {bah[i]:>8.0f}  ${c[i]:>9,.0f}  {tag}")

    print("\nOBSERVED range statistics (mechanical; headline mempool value in parens):")
    print(f"  TOP  epoch-max   day {o['top_em_day']:>6.0f}d (21)     block {o['top_em_blk']:>7.0f} (1,695)")
    print(f"  TOP  selection   day {o['top_sel_day']:>6.0f}d (21)     block {o['top_sel_blk']:>7.0f} (1,695)")
    print(f"  TOP  HOSTILE 4-top (incl 2013)   day {o['top_h4_day']:>5.0f}d          block {o['top_h4_blk']:>7.0f}")
    print(f"  BOT  after-halv  day {o['bot_det_day']:>6.0f}d (135)    block {o['bot_det_blk']:>7.0f} (5,024)")
    print(f"  BOT  top->bottom gap best-3   day {o['bot_gap_day']:>6.0f}d (37, <=42 rule)")
    print(f"  BOT  top->bottom LAG range (adversarial: bottom info beyond its top)"
          f"   day {o['bot_lag_day']:>6.0f}d   block {o['bot_lag_blk']:>7.0f}")

    # thresholds scored against = the mechanical observed values (internally consistent)
    thr = {
        "top_em_day": o["top_em_day"], "top_sel_day": o["top_sel_day"],
        "top_em_blk": o["top_em_blk"], "top_sel_blk": o["top_sel_blk"],
        "top_h4_day": o["top_h4_day"], "top_h4_blk": o["top_h4_blk"],
        "bot_det_day": o["bot_det_day"], "bot_det_blk": o["bot_det_blk"],
        "bot_lag_day": o["bot_lag_day"], "bot_lag_blk": o["bot_lag_blk"],
        "bot_gap_day": BOT_RANGE_OBS,   # 42, the paper's fixed rule
    }

    # ---------- the null ----------
    ret = np.diff(np.log(c))
    n = len(ret)
    rng = np.random.default_rng(SEED)
    print(f"\nblock-bootstrap null: B={B} per L in {LS}, SEED={SEED}, same calendar, same turn rule."
          f"\nEach path scored in BOTH day and block phase (same draws).\n")
    keys = list(thr.keys())
    hdr = ("L", "top_em_day", "top_em_blk", "top_sel_day", "top_sel_blk",
           "bot_det_day", "bot_det_blk", "bot_gap_day")
    print("  " + " ".join(f"{h:>12}" for h in hdr))
    pooled = {k: 0 for k in keys}
    nvalid = 0
    for L in LS:
        nb = int(np.ceil(n / L))
        hits = {k: 0 for k in keys}
        for _ in range(B):
            starts = rng.integers(0, n, nb)
            idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
            cp = np.empty(n + 1)
            cp[0] = 1.0
            np.cumsum(ret[idx], out=cp[1:])
            np.exp(cp[1:], out=cp[1:])
            s = score(cp, dates, epoch, dah, bah)
            nvalid += s["bot_valid"]
            for k in keys:
                if s[k] <= thr[k]:
                    hits[k] += 1
        for k in keys:
            pooled[k] += hits[k]
        row = [f"{L:>12}"] + [f"{hits[k]/B:>12.4f}" for k in hdr[1:]]
        print("  " + " ".join(row))

    NB = len(LS) * B
    print(f"\npooled over all block lengths ({NB} paths):")
    print(f"  TOP  epoch-max     day {pooled['top_em_day']:>4}/{NB}   block {pooled['top_em_blk']:>4}/{NB}")
    print(f"  TOP  selection     day {pooled['top_sel_day']:>4}/{NB}   block {pooled['top_sel_blk']:>4}/{NB}")
    print(f"  TOP  HOSTILE 4-top day {pooled['top_h4_day']:>4}/{NB}   block {pooled['top_h4_blk']:>4}/{NB}"
          f"    (E1 reconciliation: does block keep the 4-top variant more extreme?)")
    print(f"  BOT  after-halving day {pooled['bot_det_day']:>4}/{NB}   block {pooled['bot_det_blk']:>4}/{NB}"
          f"    (<- THE BOTTOMS RESCUE)")
    print(f"  BOT  gap best-3<=42 (day, empirical_null continuity)  {pooled['bot_gap_day']:>4}/{NB}")
    print(f"\nADVERSARIAL — is the bottom rarity independent of the tops, or inherited?")
    print(f"  paths with a valid 3-cycle bottom structure: {nvalid}/{NB}")
    if nvalid:
        print(f"  after-halving range CONDITIONAL on structure:  day {pooled['bot_det_day']/nvalid*100:5.1f}%"
              f"   block {pooled['bot_det_blk']/nvalid*100:5.1f}%")
    print(f"  top->bottom LAG range (bottom info beyond its own top):"
          f"  day {pooled['bot_lag_day']:>4}/{NB}   block {pooled['bot_lag_blk']:>4}/{NB}")
    print(f"    if the LAG range replicates as loosely as the gap stat (~40%), the after-halving")
    print(f"    bottom rarity is largely the TOP phase-lock propagated, not independent evidence.")
    print("\nNOTE thresholds are the mechanical real-series ranges (printed above), so the p is a"
          "\nlike-for-like null-reproduction fraction. n=3 mature epochs; treat as a weak prior.")


if __name__ == "__main__":
    main()
