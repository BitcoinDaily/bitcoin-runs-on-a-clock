"""
empirical_null_test.py — the turn-timing test under an EMPIRICAL DRAWDOWN-PROCESS null,
replacing the uniform-window null's weakest assumption.

Referee objection answered here: "large-drawdown peaks may cluster at a ~4-year cadence
naturally — the uniform null is too easy to beat." Null construction: circular block-bootstrap
of Bitcoin's own daily log returns (block length L, sensitivity grid), producing synthetic
price histories over the SAME calendar with the same return distribution, volatility
clustering, and drawdown geometry — but no alignment with the halving schedule. Each synthetic
path is processed by the IDENTICAL mechanical turn rule used on the real data (cycle top = ATH
followed by >=45% drawdown before any new high; final running peak counts if its drawdown
reaches 35%).

Selection symmetry (conservative against our claim): the observed 21d top range itself uses a
selection — epoch 3 had two qualifying tops (Apr/Nov 2021) and the tight range uses Nov. So
synthetic paths get the SAME freedom:
  TOP criterion:    >=1 qualifying top in EACH mature epoch (E2/E3/E4), and the selection of
                    one top per epoch MINIMIZING the days-after-halving range gives range <= 21d.
  BOTTOM criterion: >=3 completed top->bottom gaps anywhere in the path (real data has 5:
                    88/406/364/98/366d), and the best 3-subset range <= 42d.
  JOINT = both. Empirical p = fraction of paths at least as "clock-like" as history.

The real series is run through the same scorer first as a self-check.
"""
import numpy as np
import pandas as pd
import pl_lib

DD, DD_OPEN = 0.45, 0.35
TOP_RANGE_OBS, BOT_RANGE_OBS = 21, 42
B = 2000
LS = [30, 60, 90, 120, 250]
SEED = 31


def extract_tops(c):
    """Indices of cycle tops by the mechanical rule (vectorized)."""
    runmax = np.maximum.accumulate(c)
    prev = np.concatenate(([-np.inf], runmax[:-1]))
    ath = np.flatnonzero(c > prev)                      # strict new ATHs
    if len(ath) == 0:
        return np.array([], int)
    segmin = np.minimum.reduceat(c, ath)                # min from each ATH to next ATH
    ddv = segmin / c[ath] - 1.0
    tops = ath[ddv <= -DD]
    # final running peak: in-progress bear counts at DD_OPEN
    if ddv[-1] > -DD and ddv[-1] <= -DD_OPEN and ath[-1] not in tops:
        tops = np.append(tops, ath[-1])
    return np.sort(tops)


def score_path(c, dah, epoch, dates):
    """Return (top_ok, bot_ok, n_mature_tops, top_minrange, bot_minrange, topB_ok).

    Two top constructions:
      (A) selection-symmetric: min range over one-top-per-epoch selections (conservative bound);
      (B) epoch-max, deterministic: each epoch's HIGHEST-priced qualifying top — which, since
          every qualifying top is an ATH, is simply the LAST qualifying top in the epoch.
          Zero analyst freedom. PRIMARY statistic.
    """
    tops = extract_tops(c)
    # ---- (A) tops: one per mature epoch, min range over selections ----
    by_ep = {e: [int(dah[i]) for i in tops if epoch[i] == e] for e in (2, 3, 4)}
    top_minrange = np.inf
    if all(len(v) for v in by_ep.values()):
        for a in by_ep[2]:
            for b in by_ep[3]:
                for d in by_ep[4]:
                    r = max(a, b, d) - min(a, b, d)
                    top_minrange = min(top_minrange, r)
    n_mature = sum(len(v) for v in by_ep.values())
    # ---- (B) tops: deterministic epoch-max (= last qualifying top per epoch) ----
    topB_range = np.inf
    if all(len(v) for v in by_ep.values()):
        sel = [by_ep[e][-1] for e in (2, 3, 4)]   # last per epoch == highest price
        topB_range = max(sel) - min(sel)
    # ---- bottoms: completed top->bottom gaps, best 3-subset range ----
    gaps = []
    for k in range(len(tops) - 1):
        seg = c[tops[k]:tops[k + 1]]
        bot_i = tops[k] + int(np.argmin(seg))
        gaps.append((dates[bot_i] - dates[tops[k]]).days)
    bot_minrange = np.inf
    if len(gaps) >= 3:
        g = np.sort(np.array(gaps, float))
        bot_minrange = float(np.min(g[2:] - g[:-2]))
    return (top_minrange <= TOP_RANGE_OBS, bot_minrange <= BOT_RANGE_OBS,
            n_mature, top_minrange, bot_minrange, topB_range <= TOP_RANGE_OBS)


def main():
    df = pl_lib.load_prices()
    c = df["c"].to_numpy()
    dates = df.index
    epoch = pl_lib.epoch_of(dates)
    dah = np.full(len(df), -1.0)
    for e, hd in pl_lib.HALVINGS.items():
        m = dates >= hd
        dah[m] = (dates[m] - hd).days

    # ---- self-check on the real series ----
    t_ok, b_ok, nm, tr, br, tB_ok = score_path(c, dah, epoch, dates)
    print("self-check on REAL series:")
    print(f"  mature-epoch tops n={nm}, (A) selection min range={tr:.0f}d (<=21), "
          f"min 3-subset bottom range={br:.0f}d (<=42), (B) epoch-max criterion ok={tB_ok}")
    print(f"  top_ok={t_ok} bot_ok={b_ok}\n")
    assert t_ok and b_ok and tB_ok, "real series fails its own criterion — scoring bug"

    ret = np.diff(np.log(c))
    n = len(ret)
    rng = np.random.default_rng(SEED)
    print(f"block-bootstrap null: B={B} paths per block length, same calendar/halvings, "
          f"same turn rule, selection-symmetric scoring")
    print(f"  {'L':>5} {'B:epoch-max':>12} {'A:selection':>12} {'P(bot<=42d)':>12} "
          f"{'A joint':>9} {'avg mature tops':>16}")
    totB = totA = 0
    for L in LS:
        nb = int(np.ceil(n / L))
        top_hits = bot_hits = joint_hits = topB_hits = 0
        nm_sum = 0
        for b in range(B):
            starts = rng.integers(0, n, nb)
            idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
            cp = np.empty(n + 1)
            cp[0] = 1.0
            np.cumsum(ret[idx], out=cp[1:])
            np.exp(cp[1:], out=cp[1:])
            t_ok, b_ok, nm, _, _, tB_ok = score_path(cp, dah, epoch, dates)
            top_hits += t_ok
            bot_hits += b_ok
            joint_hits += (t_ok and b_ok)
            topB_hits += tB_ok
            nm_sum += nm
        totB += topB_hits; totA += top_hits
        print(f"  {L:>5} {topB_hits/B:>12.4f} {top_hits/B:>12.4f} {bot_hits/B:>12.4f} "
              f"{joint_hits/B:>9.4f} {nm_sum/B:>16.2f}")
    print(f"\n  pooled across block lengths: B(epoch-max) {totB}/{len(LS)*B} hits"
          f"  |  A(selection) {totA}/{len(LS)*B} hits")
    print("\ninterpretation: P(joint) is the probability that a Bitcoin-like drawdown process,"
          "\nwith NO relationship to the halving calendar, reproduces a turn regularity at least"
          "\nas tight as the one observed — under scoring that grants the null every selection"
          "\nfreedom the observed statistic enjoyed.")


if __name__ == "__main__":
    main()
