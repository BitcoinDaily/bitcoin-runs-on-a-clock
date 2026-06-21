"""
macro_study.py — confounder analysis: is the halving clock just a stand-in for the liquidity
cycle (M2) or the business cycle (yield curve)?

Identification honesty up front: the liquidity cycle and the halving cycle are roughly
co-periodic (~4y) and we have only 3-4 overlaps — a co-periodic confounder cannot be fully
"ruled out" at this n. What CAN discriminate:

  1. IC battery — M2 YoY, M2 6m-annualized, T10Y2Y level & 1y-change (publication-lagged,
     causal) in the same per-epoch framework as phase/pl_z. Stable sign across epochs, or
     unstable like the price oscillators?
  2. LEAD/LAG stability — folklore "M2 leads BTC by ~10 weeks": IC(M2 YoY shifted k days,
     fwd 90d) for a k grid, per epoch. A structural driver should show a stable best-k.
  3. TURN-TIMING precision — distance of each BTC cycle top/bottom to the nearest M2-YoY
     peak/trough vs the halving clock's 525/546/534d (+/-2%).
  4. HORSE RACE — fwd 180d returns on standardized {phase, m2_yoy, t10y2y}, Newey-West
     (lag 180), mature sample + per epoch.

Data: M2 monthly 2018+ / quarterly 2001+ (merged), T10Y2Y quarterly — via the TradingView FRED
mirror (build_macro_csv.py). Publication lag: M2 +28d; T10Y2Y +7d (quarterly sampling is itself
conservative). Macro turn DATES in test 3 are ex-post (only knowable months later) — which only
HELPS the macro side; the halving clock is known years ahead.
"""
import numpy as np
import pandas as pd
import pl_lib
from study_signals import fwd_return, spearman

EPOCH_NAME = {2: "E2_2017", 3: "E3_2021", 4: "E4_2025"}


def daily_causal(s, lag_days, idx):
    s = s.copy()
    s.index = s.index + pd.Timedelta(days=lag_days)
    return s.reindex(idx.union(s.index)).ffill().reindex(idx)


def local_turns(s, w=4, min_gap_days=270):
    """Peaks/troughs of a (quarterly/monthly) series: extreme within +/-w obs."""
    v = s.dropna()
    peaks, troughs = [], []
    for i in range(w, len(v) - w):
        win = v.iloc[i - w:i + w + 1]
        if v.iloc[i] >= win.max() and (not peaks or (v.index[i] - peaks[-1]).days > min_gap_days):
            peaks.append(v.index[i])
        if v.iloc[i] <= win.min() and (not troughs or (v.index[i] - troughs[-1]).days > min_gap_days):
            troughs.append(v.index[i])
    return peaks, troughs


def nw_ols(y, X, lag):
    Xs = np.column_stack([np.ones(len(y))] + [(x - x.mean()) / x.std() for x in X.T])
    XtX_inv = np.linalg.inv(Xs.T @ Xs)
    beta = XtX_inv @ Xs.T @ y
    u = y - Xs @ beta
    G = Xs * u[:, None]
    n = len(y)
    S = G.T @ G / n
    for j in range(1, min(lag, n - 2) + 1):
        w = 1 - j / (lag + 1)
        gj = G[j:].T @ G[:-j] / n
        S += w * (gj + gj.T)
    V = XtX_inv @ (n * S) @ XtX_inv
    return beta, beta / np.sqrt(np.diag(V))


def main():
    m2 = pd.read_csv("macro_m2.csv", parse_dates=["date"]).set_index("date")["M2SL"]
    t10 = pd.read_csv("macro_t10y2y.csv", parse_dates=["date"]).set_index("date")["T10Y2Y"]

    df = pl_lib.build_signals(pl_lib.load_close_csv("btc_daily.csv"))
    phase = np.full(len(df), np.nan)
    for e, hd in pl_lib.HALVINGS.items():
        m = df.index >= hd
        phase[m] = (df.index[m] - hd).days
    df["phase"] = phase
    for h in [30, 90, 180]:
        df[f"fwd{h}"] = fwd_return(df["c"].to_numpy(), h)

    m2d = daily_causal(m2, 28, df.index)
    df["m2_yoy"] = m2d.pct_change(365)
    df["m2_6m"] = (m2d / m2d.shift(182)) ** 2 - 1
    t10d = daily_causal(t10, 7, df.index)
    df["t10y2y"] = t10d
    df["t10_chg1y"] = t10d - t10d.shift(365)

    sigs = ["phase", "pl_z", "m2_yoy", "m2_6m", "t10y2y", "t10_chg1y"]

    print("=== 1. IC battery (macro w/ publication lags) per epoch ===")
    for h in [30, 180]:
        print(f"  fwd {h}d:")
        print(f"  {'epoch':8} " + " ".join(f"{s:>10}" for s in sigs))
        for e in [2, 3, 4]:
            sub = df[df["epoch"] == e]
            cells = []
            for s in sigs:
                d2 = sub.dropna(subset=[s, f"fwd{h}"])
                cells.append(f"{spearman(d2[s], d2[f'fwd{h}']):+.2f}" if len(d2) >= 60 else "n/a")
            print(f"  {EPOCH_NAME[e]:8} " + " ".join(f"{c:>10}" for c in cells))

    print("\n=== 2. 'M2 leads BTC' lead/lag stability — IC(m2_yoy shifted +k days, fwd90) ===")
    ks = [0, 30, 60, 90, 120, 180, 270]
    print(f"  {'epoch':8} " + " ".join(f"k={k:>4}" for k in ks))
    for e in [2, 3, 4]:
        idx_e = df.index[df["epoch"] == e]
        cells = []
        for k in ks:
            s = df["m2_yoy"].shift(k)
            d2 = pd.DataFrame({"s": s, "f": df["fwd90"]}).loc[idx_e].dropna()
            cells.append(f"{spearman(d2['s'], d2['f']):+.2f}" if len(d2) >= 60 else "  n/a")
        print(f"  {EPOCH_NAME[e]:8} " + " ".join(f"{c:>6}" for c in cells))

    print("\n=== 3. Turn timing: BTC cycle turns vs nearest M2-YoY turn vs halving clock ===")
    m2_yoy_q = m2.pct_change(4) if len(m2) < 200 else m2.pct_change(12)
    # merged series is quarterly pre-2018, monthly after; use generic offset-aware YoY:
    m2_yoy_series = (m2 / m2.shift(freq="365D").reindex(m2.index, method="nearest")) - 1
    pk, tr = local_turns(m2_yoy_series)
    print("  M2-YoY peaks:  ", ", ".join(str(p.date()) for p in pk if p.year >= 2012))
    print("  M2-YoY troughs:", ", ".join(str(t.date()) for t in tr if t.year >= 2012))
    btc_tops = [("2017-12-16", 525), ("2021-11-08", 546), ("2025-10-06", 534)]
    btc_bots = ["2015-01-14", "2018-12-15", "2022-11-09"]
    for d, ph in btc_tops:
        t = pd.Timestamp(d)
        near = min(pk, key=lambda p: abs((p - t).days))
        print(f"  TOP {d}: nearest M2-YoY peak {near.date()} ({(near-t).days:+d}d)   "
              f"halving clock: {ph}d")
    for d in btc_bots:
        t = pd.Timestamp(d)
        near = min(tr, key=lambda p: abs((p - t).days))
        print(f"  BOT {d}: nearest M2-YoY trough {near.date()} ({(near-t).days:+d}d)")
    print("  halving-clock top dispersion: 525/546/534d -> +/-10d around 535 (+/-2%)")
    print("  (M2 turns are ex-post: confirmable only months later; the halving clock is known"
          " years ahead)")

    print("\n=== 4. Horse race: fwd180 ~ phase + m2_yoy + t10y2y (NW lag=180) ===")
    sub = df[df["epoch"] >= 2].dropna(subset=["phase", "m2_yoy", "t10y2y", "fwd180"])
    beta, t = nw_ols(sub["fwd180"].to_numpy(),
                     sub[["phase", "m2_yoy", "t10y2y"]].to_numpy(float), lag=180)
    names = ["const", "phase", "m2_yoy", "t10y2y"]
    print(f"  mature sample (2016-07 ->), n={len(sub)}")
    for nm, b, tt in zip(names, beta, t):
        print(f"    {nm:8} beta={b:+.3f}  NW-t={tt:+.2f}")
    print("  regressor corr:")
    print("  " + sub[["phase", "m2_yoy", "t10y2y"]].corr().round(2).to_string().replace("\n", "\n  "))
    for e in [2, 3, 4]:
        s2 = sub[sub["epoch"] == e]
        if len(s2) < 200:
            continue
        _, t2 = nw_ols(s2["fwd180"].to_numpy(),
                       s2[["phase", "m2_yoy", "t10y2y"]].to_numpy(float), lag=180)
        print(f"  {EPOCH_NAME[e]}: " + "  ".join(
            f"{nm} t={tt:+.1f}" for nm, tt in zip(names[1:], t2[1:])))


if __name__ == "__main__":
    main()
