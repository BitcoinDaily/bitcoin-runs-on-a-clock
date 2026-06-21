"""
pl_backtest.py — Part B: tradeable R-multiple backtest of the power-law-deviation edge,
benchmarked head-to-head against the same trade STRUCTURE driven by RSI and by the Mayer
Multiple, plus buy & hold.

Edge under test: go LONG when the (causal) signal says price is stretched far BELOW its trend,
hold for the reversion, exit when price reverts to the trend (or a catastrophe stop / time stop).
Only the SIGNAL differs between the three strategies — entry/exit structure, stop, fees, universe
and period are identical, so the comparison is fair (discipline #5: no hand-picking).

Fills are INTRABAR on real Bitstamp daily OHLC (discipline #3): signal decided on a bar's close,
entered next bar's OPEN; each day the low is checked against the catastrophe stop BEFORE the
exit signal (stop-before-target tie-break). R = (exit-entry)/(entry-stop), net of round-trip fee.
"""
import argparse
import sys
import numpy as np
import pandas as pd
import pl_lib

sys.path.append(r"C:\Users\jaehe\.claude\skills\backtest-strategy\scripts")
import bt_lib  # noqa: E402

EPOCH_NAME = {0: "pre", 1: "E1_2013", 2: "E2_2017", 3: "E3_2021", 4: "E4_2025"}

# Per-signal entry/exit rules. "cheap" = stretched far below trend (LONG trigger);
# "fair" = reverted back to/above trend (EXIT). Thresholds are the SAME shape (z<-thr / z>=exit)
# for the two z-signals; RSI uses its conventional oversold/neutral bands.
SIG_RULES = {
    "pl_z":    dict(col="pl_z",    enter=lambda v, e: v < -e, exit_at=lambda v, x: v >= x),
    "mayer_z": dict(col="mayer_z", enter=lambda v, e: v < -e, exit_at=lambda v, x: v >= x),
    "rsi":     dict(col="rsi",     enter=lambda v, e: v < e,  exit_at=lambda v, x: v >= x),
}
# default exit level per signal (revert-to-mean): z->0, rsi->55
DEF_EXIT = {"pl_z": 0.0, "mayer_z": 0.0, "rsi": 55.0}
DEF_ENTER = {"pl_z": 1.0, "mayer_z": 1.0, "rsi": 30.0}


def backtest(df, signal, enter_thr, exit_thr, stop_pct, max_hold, fee, cooldown=5):
    rule = SIG_RULES[signal]
    col = rule["col"]
    o = df["o"].to_numpy(); h = df["h"].to_numpy(); l = df["l"].to_numpy(); c = df["c"].to_numpy()
    sig = df[col].to_numpy()
    dates = df.index
    ep = df["epoch"].to_numpy()
    N = len(df)
    trades = []
    i = 0
    last_exit = -10**9
    while i < N - 1:
        # signal decided on close of bar i, act on open of bar i+1
        if (not np.isnan(sig[i]) and rule["enter"](sig[i], enter_thr)
                and (i - last_exit) >= cooldown):
            entry_i = i + 1
            entry_px = o[entry_i]
            stop_px = entry_px * (1 - stop_pct)
            risk = entry_px - stop_px
            exit_px = exit_i = reason = None
            mfe = mae = 0.0
            for j in range(entry_i, min(entry_i + max_hold, N)):
                mfe = max(mfe, (h[j] - entry_px) / risk)
                mae = min(mae, (l[j] - entry_px) / risk)
                if l[j] <= stop_px:                       # catastrophe stop (intrabar low)
                    exit_px, exit_i, reason = stop_px, j, "stop"
                    break
                if not np.isnan(sig[j]) and rule["exit_at"](sig[j], exit_thr):
                    # revert-to-trend: exit next open after the signal closes
                    k = min(j + 1, N - 1)
                    exit_px, exit_i, reason = o[k], k, "revert"
                    break
            if exit_px is None:                            # time stop
                exit_i = min(entry_i + max_hold, N - 1)
                exit_px, reason = c[exit_i], "time"
            R = (exit_px - entry_px) / risk - 2 * fee * entry_px / risk
            trades.append(dict(
                coin="BTC", side="long", signal=signal, entry_dt=dates[entry_i],
                entry_px=entry_px, stop_px=stop_px, exit_px=exit_px, R=R, reason=reason,
                bars_held=exit_i - entry_i, mfe=round(mfe, 2), mae=round(mae, 2),
                epoch=int(ep[entry_i]), epoch_name=EPOCH_NAME[int(ep[entry_i])],
                sig_at_entry=round(float(sig[i]), 2)))
            last_exit = exit_i
            i = exit_i + 1
        else:
            i += 1
    return pd.DataFrame(trades)


def buy_hold_R(df, stop_pct, fee):
    """Buy&hold expressed in the same R units (one trade, entry day-1 open to last close)."""
    o = df["o"].to_numpy(); c = df["c"].to_numpy()
    entry = o[1]; risk = entry * stop_pct
    R = (c[-1] - entry) / risk - 2 * fee * entry / risk
    return R


def per_epoch_report(tr):
    print("  per-epoch:")
    for e in [1, 2, 3, 4]:
        g = tr[tr["epoch"] == e]
        if len(g) == 0:
            print(f"    {EPOCH_NAME[e]:9} n=0"); continue
        m = bt_lib.metrics(g)["all"]
        print(f"    {EPOCH_NAME[e]:9} n={m['n']:3d} win={m['win']:5.1f}% PF={m['pf']:5.2f} "
              f"avgR={m['avgR']:+.3f} totR={m['totR']:+7.1f} maxDD={m['maxDD']:+6.1f} "
              f"Sharpe={m['sharpe']:+.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", default="pl_z", choices=list(SIG_RULES))
    ap.add_argument("--enter-thr", type=float, default=None)
    ap.add_argument("--exit-thr", type=float, default=None)
    ap.add_argument("--stop-pct", type=float, default=0.35)
    ap.add_argument("--max-hold", type=int, default=540)
    ap.add_argument("--fee", type=float, default=0.0015)
    ap.add_argument("--cooldown", type=int, default=5)
    ap.add_argument("--compare", action="store_true", help="run all three signals + buy&hold")
    ap.add_argument("--autopsy", action="store_true")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    df = pl_lib.build_signals(pl_lib.load_prices())
    bh = buy_hold_R(df, args.stop_pct, args.fee)

    sigs = list(SIG_RULES) if args.compare else [args.signal]
    print(f"period {df.index.min().date()} -> {df.index.max().date()}  stop={args.stop_pct:.0%} "
          f"max_hold={args.max_hold}d fee={args.fee:.2%}/side")
    print(f"buy&hold (same R units, 1 trade): {bh:+.1f}R\n")

    all_tr = []
    for s in sigs:
        en = args.enter_thr if args.enter_thr is not None else DEF_ENTER[s]
        ex = args.exit_thr if args.exit_thr is not None else DEF_EXIT[s]
        tr = backtest(df, s, en, ex, args.stop_pct, args.max_hold, args.fee, args.cooldown)
        if len(tr) == 0:
            print(f"### {s}: no trades"); continue
        tr["sig"] = s
        all_tr.append(tr)
        print(f"########## SIGNAL = {s}  (enter {('z<-'+str(en)) if s!='rsi' else 'rsi<'+str(en)}, "
              f"exit {('z>='+str(ex)) if s!='rsi' else 'rsi>='+str(ex)}) ##########")
        print(bt_lib.fmt_metrics(bt_lib.metrics(tr)))
        print(bt_lib.assess(bt_lib.metrics(tr)))
        per_epoch_report(tr)
        if args.autopsy:
            print("  --- loss autopsy ---")
            bt_lib.autopsy_table(tr, key="reason", label="exit reason")
            bt_lib.autopsy_table(tr, key="epoch_name", label="epoch")
            bt_lib.autopsy_table(tr, fn=lambda t: t["sig_at_entry"], bins=4, label="entry-signal depth")
            bt_lib.autopsy_table(tr, fn=lambda t: t["bars_held"], bins=4, label="hold length (days)")
        print()

    if args.csv and all_tr:
        pd.concat(all_tr).to_csv(args.csv, index=False)
        print(f"saved trades -> {args.csv}")


if __name__ == "__main__":
    main()
