"""
clock_timing_backtest.py — the REAL "timing the cycle vs just holding" backtest behind
Video 1's CH2 / chart C10 and the script's FACTS SHEET (§2 of VIDEO1_HANDOFF.md).

THE RULE (fully causal — halving dates are known years in advance):
  position = CASH  when  SELL_DAY <= days-since-most-recent-halving <= BUY_DAY   (sit out the bust)
           = LONG  otherwise                                                     (ride the boom)
  Position is decided on a day's close and held from the NEXT day's close (1-day lag), so there is
  zero look-ahead. The only inputs are the halving calendar and the price you already saw.

WHY THIS REPLACES THE OLD CHART:
  C10 used to be the "Sharpe crossover" from exposure_study.py (the -0.99/-0.41/-0.26/+0.12
  per-epoch Sharpe edge). That framed the edge as "timing finally beat holding only THIS cycle,"
  which is wrong: real halving-clock timing beat buy-and-hold in EVERY cycle, on both return and
  drawdown. This script is the honest measurement; C10 is rebuilt from its output.

A "cycle" = one halving epoch: [halving_N, halving_{N+1}) , and [last halving, end] for the live
one. Buy-and-hold = close at the halving to the close at the next halving (or last close).

Run from PowerLaw/:
  python clock_timing_backtest.py
  python clock_timing_backtest.py --sell 525 --buy 900          # change the window
  python clock_timing_backtest.py --robust                      # sweep nearby sell/buy days
"""
import argparse
import numpy as np
import pandas as pd
import pl_lib

EPOCH_TOPYEAR = {1: "2013", 2: "2017", 3: "2021", 4: "2025"}


def days_since_halving(dates):
    """Days since the MOST RECENT halving for each date (NaN before the first halving)."""
    dates = pd.DatetimeIndex(dates)
    dsh = np.full(len(dates), np.nan)
    for e, h in pl_lib.HALVINGS.items():
        m = dates >= h
        dsh[m] = (dates[m] - h).days
    return dsh


def epoch_window(e):
    """[start, end) date bounds for halving epoch e (end = next halving, or None for the live one)."""
    start = pl_lib.HALVINGS[e]
    end = pl_lib.HALVINGS.get(e + 1)  # None for the last (live) epoch
    return start, end


def max_drawdown(equity):
    """Worst peak-to-trough drop of an equity curve (a negative number)."""
    eq = np.asarray(equity, float)
    if len(eq) == 0:
        return np.nan
    peak = np.maximum.accumulate(eq)
    return float((eq / peak - 1.0).min())


def run(df, sell_day, buy_day):
    """Attach the causal clock position + daily strategy/buy-hold returns to a copy of df."""
    df = df.copy()
    dsh = days_since_halving(df.index)
    in_cash = (dsh >= sell_day) & (dsh <= buy_day)          # sit out the bust window
    pos = np.where(np.isnan(dsh), 1.0, np.where(in_cash, 0.0, 1.0))  # pre-first-halving = long
    df["pos"] = pd.Series(pos, index=df.index).shift(1).fillna(1.0)  # causal: hold from next day
    df["ret"] = df["c"].pct_change().fillna(0.0)
    df["bh_ret"] = df["ret"]
    df["st_ret"] = df["pos"] * df["ret"]
    df["epoch"] = pl_lib.epoch_of(df.index)
    return df


def per_cycle(df):
    """Per-epoch total return + max drawdown, strategy vs buy-and-hold, plus the all-stacked roll-up."""
    rows = []
    for e in [1, 2, 3, 4]:
        start, end = epoch_window(e)
        m = (df.index >= start) if end is None else ((df.index >= start) & (df.index < end))
        sub = df.loc[m]
        if len(sub) < 5:
            continue
        bh_eq = (1 + sub["bh_ret"]).cumprod()
        st_eq = (1 + sub["st_ret"]).cumprod()
        rows.append(dict(
            epoch=e, top_year=EPOCH_TOPYEAR[e],
            start=start.date(), end=(end.date() if end else sub.index[-1].date()),
            days=len(sub), tim=float(sub["pos"].mean()),
            bh_ret=float(bh_eq.iloc[-1] - 1), st_ret=float(st_eq.iloc[-1] - 1),
            bh_dd=max_drawdown(bh_eq), st_dd=max_drawdown(st_eq),
        ))
    return pd.DataFrame(rows)


def stacked(df):
    """Whole-history compounding: final wealth multiple of timing vs hold, and each one's worst DD."""
    bh_eq = (1 + df["bh_ret"]).cumprod()
    st_eq = (1 + df["st_ret"]).cumprod()
    return dict(
        bh_mult=float(bh_eq.iloc[-1]), st_mult=float(st_eq.iloc[-1]),
        ratio=float(st_eq.iloc[-1] / bh_eq.iloc[-1]),
        bh_dd=max_drawdown(bh_eq), st_dd=max_drawdown(st_eq),
        start=df.index[0].date(), end=df.index[-1].date(),
    )


def report(df, sell_day, buy_day):
    pc = per_cycle(df)
    print(f"\nCLOCK-TIMING vs BUY-AND-HOLD   (cash when {sell_day} <= days-since-halving <= {buy_day}, "
          f"else long; causal 1-day lag)")
    print(f"data {df.index[0].date()} -> {df.index[-1].date()}   ({len(df)} days)")
    print("=" * 92)
    print(f"  {'cycle':>6} {'window':>25} {'time-in':>8} "
          f"{'TIMING ret':>12} {'HOLD ret':>12} {'TIMING dd':>10} {'HOLD dd':>9}")
    for _, r in pc.iterrows():
        print(f"  {r['top_year']:>6} {str(r['start'])+'..'+str(r['end']):>25} {r['tim']*100:6.0f}%  "
              f"{r['st_ret']*100:+11,.0f}% {r['bh_ret']*100:+11,.0f}% "
              f"{r['st_dd']*100:+9.0f}% {r['bh_dd']*100:+8.0f}%")
    st = stacked(df)
    print("-" * 92)
    print(f"  ALL CYCLES STACKED: timing made {st['st_mult']:,.0f}x vs hold {st['bh_mult']:,.0f}x "
          f"=  {st['ratio']:.1f}x more money than holding")
    print(f"  WORST CRASH (max drawdown):  timing {st['st_dd']*100:.0f}%   vs   hold {st['bh_dd']*100:.0f}%")
    print("=" * 92)
    wins_ret = (pc["st_ret"] > pc["bh_ret"]).sum()
    wins_dd = (pc["st_dd"] > pc["bh_dd"]).sum()  # less negative = shallower = better
    print(f"  timing beat hold on RETURN in {wins_ret}/{len(pc)} cycles, "
          f"on DRAWDOWN in {wins_dd}/{len(pc)} cycles.")
    return pc, st


def robust(df_raw):
    """Sweep sell-day (505..545) x buy-day (860..940): confirm the verdict is not knife-edge."""
    print("\nROBUSTNESS SWEEP — all-stacked ratio (x more than hold) and #cycles timing wins on return")
    print("  sell\\buy", "  ".join(f"{b:>6}" for b in range(860, 941, 20)))
    for s in range(505, 546, 10):
        cells = []
        for b in range(860, 941, 20):
            d = run(df_raw, s, b)
            pc = per_cycle(d); st = stacked(d)
            wins = int((pc["st_ret"] > pc["bh_ret"]).sum())
            cells.append(f"{st['ratio']:4.0f}x/{wins}")
        print(f"  {s:>5}   ", "  ".join(f"{c:>6}" for c in cells))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sell", type=int, default=525, help="cash starts this many days after the halving")
    ap.add_argument("--buy", type=int, default=900, help="cash ends this many days after the halving")
    ap.add_argument("--robust", action="store_true", help="sweep nearby sell/buy days")
    ap.add_argument("--json", default=None, help="write the locked per-cycle result to this path")
    args = ap.parse_args()

    df_raw = pl_lib.load_prices()
    df = run(df_raw, args.sell, args.buy)
    pc, st = report(df, args.sell, args.buy)

    if args.robust:
        robust(df_raw)

    if args.json:
        import json
        out = dict(sell_day=args.sell, buy_day=args.buy,
                   data_start=str(df.index[0].date()), data_end=str(df.index[-1].date()),
                   cycles=pc.to_dict(orient="records"), stacked=st)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, default=str)
        print(f"\nlocked result -> {args.json}")


if __name__ == "__main__":
    main()
