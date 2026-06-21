"""
joint_replication_test.py — EMPIRICAL joint-replication probability, replacing the analytic
back-of-envelope (9 x 0.025^2 ~= 0.006) that previously stood in for it.

Claim under test: "pl_z@180d is the only cell in the 3-signal x 3-horizon grid that is
significant with consistent sign in BOTH epoch 3 and epoch 4." How often would ANY cell achieve
that under a null where signals have no predictive relationship to future returns — while
preserving (a) each series' autocorrelation, (b) the cross-correlation BETWEEN the three
signals, and (c) the overlap structure of forward returns?

Null construction: within each epoch, circularly rotate the forward-return series relative to
the signal block by a random offset (>= max horizon away from zero), using ONE shared offset
fraction per epoch per replicate so the cross-cell dependence within an epoch is preserved.
Rotation preserves the marginal and autocorrelation structure of both sides and the cross-signal
correlations exactly; it destroys only the signal->future alignment. E3 and E4 offsets are drawn
independently (the epochs are disjoint samples).

Cell statistic: the same Newey-West rank-on-rank t (lag = horizon) used in the paper.
Hit criterion (same as the observed claim): |t| >= 1.96 in BOTH epochs with the same IC sign.
Empirical p = fraction of replicates in which ANY of the 9 cells double-hits.
Also reported: per-epoch null rejection rates (NW calibration check — the reason the analytic
number could not be trusted) and the per-cell double-hit rates.
"""
import numpy as np
import pl_lib
from study_signals import fwd_return

SIGNALS = ["pl_z", "mayer_z", "rsi"]
HORIZONS = [30, 90, 180]
TCRIT = 1.96
B = 2000
SEED = 23


def std_ranks(x):
    r = np.empty(len(x))
    r[np.argsort(x, kind="stable")] = np.arange(1, len(x) + 1, dtype=float)
    r -= r.mean()
    s = r.std()
    return r / (s if s > 0 else 1.0)


def nw_t(x, y, lag):
    n = len(x)
    beta = float(np.mean(x * y))
    u = y - beta * x
    g = x * u
    lag = min(lag, n - 2)
    omega = float(np.mean(g * g))
    for j in range(1, lag + 1):
        omega += 2.0 * (1.0 - j / (lag + 1.0)) * float(np.mean(g[j:] * g[:-j]))
    se = np.sqrt(max(omega, 1e-12) / n)
    return beta, beta / se


def main():
    rng = np.random.default_rng(SEED)
    df = pl_lib.build_signals(pl_lib.load_prices())
    for h in HORIZONS:
        df[f"fwd{h}"] = fwd_return(df["c"].to_numpy(), h)

    # pre-extract standardized ranks per (epoch, horizon)
    data = {}
    for e in [3, 4]:
        for h in HORIZONS:
            sub = df[df["epoch"] == e].dropna(subset=SIGNALS + [f"fwd{h}"])
            data[(e, h)] = (
                {s: std_ranks(sub[s].to_numpy()) for s in SIGNALS},
                std_ranks(sub[f"fwd{h}"].to_numpy()),
                len(sub),
            )

    # observed cells
    print("observed cells (NW rank-t, lag=h):")
    obs_hits = []
    for s in SIGNALS:
        for h in HORIZONS:
            (X3, y3, n3) = data[(3, h)]
            (X4, y4, n4) = data[(4, h)]
            b3, t3 = nw_t(X3[s], y3, h)
            b4, t4 = nw_t(X4[s], y4, h)
            hit = abs(t3) >= TCRIT and abs(t4) >= TCRIT and np.sign(b3) == np.sign(b4)
            if hit:
                obs_hits.append(f"{s}@{h}d")
            print(f"  {s:8} h={h:>3}  E3 t={t3:+.2f}  E4 t={t4:+.2f}  "
                  f"{'<<< double-hit' if hit else ''}")
    print(f"observed double-hits: {obs_hits}\n")

    # null replicates
    print(f"running {B} dependence-preserving rotation replicates ...")
    any_hit = 0
    cell_hits = {(s, h): 0 for s in SIGNALS for h in HORIZONS}
    epoch_rej = {3: 0, 4: 0}
    n_cells_checked = 0
    for b in range(B):
        fr = {e: rng.uniform(0.15, 0.85) for e in [3, 4]}   # shared offset frac per epoch
        hit_this = False
        for s in SIGNALS:
            for h in HORIZONS:
                ts = {}
                bs = {}
                for e in [3, 4]:
                    X, y, n = data[(e, h)]
                    k = int(fr[e] * n)
                    k = min(max(k, h), n - h)               # stay >= h from alignment
                    yr = np.roll(y, k)
                    beta, t = nw_t(X[s], yr, h)
                    ts[e] = t; bs[e] = beta
                    epoch_rej[e] += abs(t) >= TCRIT
                    n_cells_checked += 1
                if (abs(ts[3]) >= TCRIT and abs(ts[4]) >= TCRIT
                        and np.sign(bs[3]) == np.sign(bs[4])):
                    cell_hits[(s, h)] += 1
                    hit_this = True
        any_hit += hit_this
        if (b + 1) % 500 == 0:
            print(f"  {b+1}/{B}  running p(any double-hit) = {any_hit/(b+1):.4f}")

    p_emp = any_hit / B
    se = np.sqrt(p_emp * (1 - p_emp) / B)
    print(f"\nEMPIRICAL joint-replication p = {p_emp:.4f}  (MC se {se:.4f}, B={B})")
    print(f"  [analytic envelope was 9 x 0.025^2 = 0.0056 — replace it with this number]")
    rej3 = epoch_rej[3] / (n_cells_checked / 2)
    rej4 = epoch_rej[4] / (n_cells_checked / 2)
    print(f"  NW calibration under null: P(|t|>=1.96) per cell  E3={rej3:.3f}  E4={rej4:.3f}"
          f"   (nominal 0.05 — divergence here is why the analytic number was unsafe)")
    print("  per-cell double-hit rates under null:")
    for (s, h), c in sorted(cell_hits.items(), key=lambda kv: -kv[1]):
        print(f"    {s:8} h={h:>3}  {c/B:.4f}")


if __name__ == "__main__":
    main()
