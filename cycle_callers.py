"""
cycle_callers.py — the famous "never missed a top/bottom" indicators, tested honestly.

Battery (canonical PUBLISHED thresholds, fixed before looking at results — these are the
community's own trading rules, not ours):
  TOP callers   : Pi Cycle Top (111DMA crosses above 2x350DMA), MVRV > 3.7, Mayer > 2.4,
                  Puell > 4.0, price > 5 x 2yr MA
  BOTTOM callers: MVRV < 1.0, Mayer < 0.8, Puell < 0.5, price <= 200-week MA, price <= 2yr MA

Three studies:
  A. HIT/MISS table — did each trigger fire within +/-90d of each cycle's actual top/bottom
     (extracted from the data itself)? The folklore: they all nailed 2013/2017/(2021) then
     went silent at the latest peak.
  B. EXTREMES table — each indicator's per-cycle peak value. If the maxima decline monotonically,
     ANY threshold calibrated on past cycles must eventually stop firing: that is the mechanism
     of "price indicators only get worse each cycle", quantified.
  C. TIME table + IC — days-from-halving of each top/bottom (does Satoshi's 210,000-block clock
     cluster them?), and `phase` (days since halving — a PURE TIME signal, zero price input)
     added to the IC battery next to every price indicator, per epoch.

Data: Coin Metrics extended (price + MVRV + issuance), 2010-07 -> present.
"""
import numpy as np
import pandas as pd
import pl_lib
from study_signals import fwd_return, spearman

H = pl_lib.HALVINGS
EPOCH_NAME = {1: "E1_2013", 2: "E2_2017", 3: "E3_2021", 4: "E4_2025"}


def build(path="btc_metrics.csv"):
    raw = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = pd.DataFrame(index=raw.index)
    c = raw["PriceUSD"].astype(float)
    df["c"] = c
    df["o"] = c; df["h"] = c; df["l"] = c; df["v"] = np.nan
    df["t"] = (df.index - pl_lib.GENESIS).days.astype(float)
    df = df[df["c"] > 0]
    c = df["c"]

    sma = lambda n: c.rolling(n, min_periods=n).mean()
    df["pi"] = sma(111) / (2 * sma(350))
    df["mayer"] = c / sma(200)
    df["p200w"] = c / sma(1400)
    df["mult2y"] = c / sma(730)
    df["mvrv"] = raw["CapMVRVCur"].reindex(df.index).replace(0, np.nan)
    iss = raw["IssTotUSD"].reindex(df.index).replace(0, np.nan)
    df["puell"] = iss / iss.rolling(365, min_periods=365).mean()
    df["rsi"] = pl_lib.wilder_rsi(c.to_numpy(), 14)
    _, _, r = pl_lib.causal_powerlaw(df)
    df["pl_z"] = pl_lib.expanding_z(r)
    df["epoch"] = pl_lib.epoch_of(df.index)

    # pure-time signal: days since the most recent halving (NaN before the first)
    phase = np.full(len(df), np.nan)
    for e, hd in H.items():
        m = df.index >= hd
        phase[m] = (df.index[m] - hd).days
    df["phase"] = phase
    return df


def cycle_turns(df, dd=0.45, dd_open=0.35):
    """Mechanical cycle-turn definition, no hand-picking:
    a CYCLE TOP is an all-time-high followed by a >= dd (45%) drawdown before any new high
    (i.e., the peaks that define bear markets). The final running peak counts as a top
    '(in progress)' if the drawdown since it has reached dd_open. BOTTOMS = the min close
    between consecutive tops; the bottom after the last top is TBD while the bear runs."""
    c = df["c"]
    tops = []
    run_max, peak_date, cur_min = -np.inf, None, np.inf
    for dt, px in c.items():
        if px > run_max:
            if peak_date is not None and cur_min <= run_max * (1 - dd):
                tops.append(peak_date)
            run_max, peak_date, cur_min = px, dt, px
        else:
            cur_min = min(cur_min, px)
    open_bear = False
    if peak_date is not None and peak_date not in tops:
        if cur_min <= run_max * (1 - dd):
            tops.append(peak_date)
        elif cur_min <= run_max * (1 - dd_open):
            tops.append(peak_date); open_bear = True
    bottoms = []
    for a, b in zip(tops[:-1], tops[1:]):
        bottoms.append(df.loc[a:b, "c"].idxmin())
    return tops, bottoms, open_bear


def fires(cond, gap_days=45):
    """First day of each True-run, merging runs separated by < gap_days."""
    s = cond.fillna(False)
    enter = s & ~s.shift(1, fill_value=False)
    dates = list(s.index[enter])
    out = []
    for d in dates:
        if not out or (d - out[-1]).days >= gap_days:
            out.append(d)
    return out

TOP_TRIGGERS = {
    "PiCycle cross":  lambda d: (d["pi"] >= 1.0),
    "MVRV > 3.7":     lambda d: (d["mvrv"] >= 3.7),
    "Mayer > 2.4":    lambda d: (d["mayer"] >= 2.4),
    "Puell > 4.0":    lambda d: (d["puell"] >= 4.0),
    "px > 5x 2yrMA":  lambda d: (d["mult2y"] >= 5.0),
}
BOT_TRIGGERS = {
    "MVRV < 1.0":     lambda d: (d["mvrv"] <= 1.0),
    "Mayer < 0.8":    lambda d: (d["mayer"] <= 0.8),
    "Puell < 0.5":    lambda d: (d["puell"] <= 0.5),
    "px <= 200W MA":  lambda d: (d["p200w"] <= 1.0),
    "px <= 2yr MA":   lambda d: (d["mult2y"] <= 1.0),
}


def hitmiss(df, triggers, turns, hit_window=60, search_window=270):
    """For each trigger x turn: offset of the NEAREST fire within +/-search_window days
    (so we can see degradation, e.g. 'fired 211d early'); HIT if |offset| <= hit_window;
    'no fire' if nothing within the search window at all."""
    head = "  {:14}".format("trigger") + "".join(f"  {t.date()!s:>16}" for t in turns)
    print(head)
    for name, cond in triggers.items():
        fs = fires(cond(df))
        cells = []
        for t in turns:
            near = [f for f in fs if abs((f - t).days) <= search_window]
            if near:
                off = (min(near, key=lambda f: abs((f - t).days)) - t).days
                cells.append(f"HIT {off:+d}d" if abs(off) <= hit_window else f"{off:+d}d")
            else:
                cells.append("no fire")
        print("  {:14}".format(name) + "".join(f"  {c:>16}" for c in cells))


def main():
    df = build()
    tops, bottoms, open_bear = cycle_turns(df)

    print(f"data {df.index.min().date()} -> {df.index.max().date()}")
    print("\n=== cycle turns (mechanical: top = ATH followed by >=45% drawdown) ===")
    for t in tops:
        hs = [h for h in H.values() if h <= t]
        days_h = (t - max(hs)).days if hs else -1
        tag = "  (bear in progress)" if (open_bear and t == tops[-1]) else ""
        print(f"  TOP    {t.date()}  ${df.loc[t,'c']:>10,.0f}   "
              f"{days_h:>4d} days after halving{tag}")
    for i, b in enumerate(bottoms):
        hs = [h for h in H.values() if h <= b]
        days_h = (b - max(hs)).days if hs else -1
        days_t = (b - tops[i]).days
        print(f"  BOTTOM {b.date()}  ${df.loc[b,'c']:>10,.0f}   "
              f"{days_h:>4d} days after halving, {days_t} after its top")
    print("  current-cycle BOTTOM: TBD (bear in progress)" if open_bear else "")
    gaps = [(H[i + 1] - H[i]).days for i in [1, 2, 3]]
    print(f"  halving gaps: {gaps} days (210,000 blocks x ~10min = ~1,458d; Satoshi 2009-01-08: "
          f"'the amount cut in half every 4 years')")

    print("\n=== A1. TOP callers vs actual cycle tops (canonical thresholds, +/-90d window) ===")
    hitmiss(df, TOP_TRIGGERS, tops)
    print("\n=== A2. BOTTOM callers vs actual cycle bottoms ===")
    hitmiss(df, BOT_TRIGGERS, bottoms)

    print("\n=== B. per-cycle indicator EXTREMES (the decay mechanism) ===")
    print("  TOP side (max within epoch):")
    print(f"  {'epoch':8} {'pi':>6} {'mvrv':>6} {'mayer':>6} {'puell':>6} {'mult2y':>7} "
          f"{'p200w':>7}")
    for e in [1, 2, 3, 4]:
        sub = df[df["epoch"] == e]
        print(f"  {EPOCH_NAME[e]:8} " + " ".join(
            f"{sub[k].max():>6.2f}" for k in ["pi", "mvrv", "mayer", "puell"])
            + f" {sub['mult2y'].max():>7.2f} {sub['p200w'].max():>7.2f}")
    print("  BOTTOM side (min within epoch):")
    print(f"  {'epoch':8} {'mvrv':>6} {'mayer':>6} {'puell':>6} {'mult2y':>7} {'p200w':>7}")
    for e in [1, 2, 3, 4]:
        sub = df[df["epoch"] == e]
        print(f"  {EPOCH_NAME[e]:8} " + " ".join(
            f"{sub[k].min():>6.2f}" for k in ["mvrv", "mayer", "puell"])
            + f" {sub['mult2y'].min():>7.2f} {sub['p200w'].min():>7.2f}")

    print("\n=== C. IC battery incl. the PURE-TIME signal (phase = days since halving) ===")
    for h in [30, 180]:
        df[f"fwd{h}"] = fwd_return(df["c"].to_numpy(), h)
    sigs = ["phase", "pl_z", "mvrv", "puell", "pi", "mayer", "mult2y", "p200w", "rsi"]
    for h in [30, 180]:
        print(f"  fwd {h}d:")
        print(f"  {'epoch':8} " + " ".join(f"{s:>7}" for s in sigs))
        for e in [2, 3, 4]:
            sub = df[df["epoch"] == e]
            cells = []
            for s in sigs:
                d2 = sub.dropna(subset=[s, f"fwd{h}"])
                cells.append(f"{spearman(d2[s], d2[f'fwd{h}']):+.2f}" if len(d2) >= 60 else "n/a")
            print(f"  {EPOCH_NAME[e]:8} " + " ".join(f"{c:>7}" for c in cells))


if __name__ == "__main__":
    main()
