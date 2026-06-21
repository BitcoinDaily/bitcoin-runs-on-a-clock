"""
verify_hardening.py — referee-hardening of the paper's load-bearing numbers.

A. PERMUTATION VARIANTS — full transparency on every analyst choice:
   (i)   mature tops only (E2-E4: 525/546/534, range 21d)     [the paper's headline]
   (ii)  E1 top INCLUDED (371/525/546/534, range 175d)         [the hostile variant: keeps the
         first-cycle point that does NOT fit, symmetric with keeping the E1 bottom]
   (iii) bottoms (406/364/366, range 42d)
   (iv)  joints, across the full window grid.
   Interpretation note printed with the table: turns were identified EX POST by a mechanical
   rule; these are retrospective-regularity probabilities, not forecasting track records.
   Under the null the two gaps (halving->top, top->bottom) are disjoint uniforms, so the joint
   is their product BY CONSTRUCTION OF THE NULL (stated, not assumed away).

B. MULTIPLE-COMPARISONS — the full HAC/bootstrap grid (3 signals x 3 horizons x 4 epochs =
   36 cells), Benjamini-Hochberg FDR at q=0.05 and q=0.10, plus the joint-replication
   statistic: under a global null with 9 (signal,horizon) cells per epoch, the chance that
   ANY cell is significant at 5% (right sign) in BOTH E3 and E4 is ~ 9 * 0.025^2 (one-sided).
"""
import numpy as np
import pandas as pd
import pl_lib
from study_signals import fwd_return
from ic_significance import nw_tstat, block_boot, boot_p, B

SIGNALS = ["pl_z", "mayer_z", "rsi"]
HORIZONS = [30, 90, 180]
EPOCH_NAME = {1: "E1", 2: "E2", 3: "E3", 4: "E4"}


def p_range_uniform(r, W, n):
    x = r / W
    return n * x ** (n - 1) - (n - 1) * x ** n


def part_a():
    print("=== A. PERMUTATION VARIANTS (retrospective-regularity p, NOT a track record) ===")
    variants = {
        "tops mature-only (n=3, r=21)": (21, 3),
        "tops incl. E1   (n=4, r=175)": (175, 4),
        "bottoms         (n=3, r=42)": (42, 3),
    }
    Ws = [1458, 1100, 900, 700]
    print(f"  {'variant':32}" + "".join(f"  W={w:<6}" for w in Ws))
    ps = {}
    for name, (r, n) in variants.items():
        row = [p_range_uniform(r, W if n == 3 else W, n) for W in Ws]
        # bottoms live on a shorter natural window; use 800/700/600/500 for them
        if "bottoms" in name:
            row = [p_range_uniform(r, W, n) for W in [800, 700, 600, 500]]
        ps[name] = row
        print(f"  {name:32}" + "".join(f"  {p:<8.4f}" for p in row))
    print("\n  JOINT (tops x bottoms; product valid because the null draws the two gaps")
    print("  independently by construction):")
    for tag, tkey in [("headline (mature tops)", "tops mature-only (n=3, r=21)"),
                      ("HOSTILE (E1 top incl.)", "tops incl. E1   (n=4, r=175)")]:
        gen = ps[tkey][0] * ps["bottoms         (n=3, r=42)"][0]
        con = ps[tkey][-1] * ps["bottoms         (n=3, r=42)"][-1]
        print(f"    {tag:24} generous {gen:.2e}   most-conservative {con:.2e}")


def part_b():
    print("\n=== B. MULTIPLE COMPARISONS — full 36-cell grid, BH-FDR ===")
    rng = np.random.default_rng(7)
    df = pl_lib.build_signals(pl_lib.load_prices())
    for k in HORIZONS:
        df[f"fwd{k}"] = fwd_return(df["c"].to_numpy(), k)
    rows = []
    for h in HORIZONS:
        for e in [1, 2, 3, 4]:
            sub = df[df["epoch"] == e].dropna(subset=SIGNALS + [f"fwd{h}"])
            n = len(sub)
            if n < 60:
                continue
            fwd = sub[f"fwd{h}"].to_numpy()
            sigs = {s: sub[s].to_numpy() for s in SIGNALS}
            L = max(10, min(h, n // 5))
            boots, _, _ = block_boot(sigs, fwd, L, rng)
            for s in SIGNALS:
                ic, t = nw_tstat(sigs[s], fwd, lag=h)
                p = max(boot_p(boots[s]), 1.0 / B)
                rows.append(dict(signal=s, h=h, epoch=e, ic=ic, t=t, p=p))
    res = pd.DataFrame(rows)
    m = len(res)
    res = res.sort_values("p").reset_index(drop=True)
    res["rank"] = np.arange(1, m + 1)
    for q in [0.05, 0.10]:
        res[f"bh{int(q*100)}"] = res["p"] <= q * res["rank"] / m
        kmax = res.index[res[f"bh{int(q*100)}"]].max() if res[f"bh{int(q*100)}"].any() else -1
        surv = res.iloc[:kmax + 1] if kmax >= 0 else res.iloc[0:0]
        names = [f"{r.signal}@{r.h}d/{EPOCH_NAME[r.epoch]}(p={r.p:.3f})"
                 for r in surv.itertuples()]
        print(f"  BH-FDR q={q}: {len(surv)}/{m} cells survive"
              + (": " + ", ".join(names) if names else ""))
    print("\n  top-10 cells by p:")
    for r in res.head(10).itertuples():
        print(f"    {r.signal:8} h={r.h:>3} {EPOCH_NAME[r.epoch]}  IC={r.ic:+.2f}  "
              f"NW-t={r.t:+.2f}  p={r.p:.3f}")
    # joint replication: same (signal,horizon) cell significant at 5% w/ same sign in E3 AND E4
    print("\n  joint-replication check (same cell sig. at 5%, same sign, in BOTH E3 and E4):")
    hits = []
    for s in SIGNALS:
        for h in HORIZONS:
            c3 = res[(res.signal == s) & (res.h == h) & (res.epoch == 3)]
            c4 = res[(res.signal == s) & (res.h == h) & (res.epoch == 4)]
            if len(c3) and len(c4):
                if (c3.p.iloc[0] < .05 and c4.p.iloc[0] < .05
                        and np.sign(c3.ic.iloc[0]) == np.sign(c4.ic.iloc[0])):
                    hits.append(f"{s}@{h}d (p={c3.p.iloc[0]:.3f}, {c4.p.iloc[0]:.3f})")
    exp = 9 * 0.025 ** 2
    print(f"    observed: {hits if hits else 'none'}")
    print(f"    expected under global null (9 cells, one-sided 2.5% each epoch): "
          f"{exp:.4f} cells -> P(>=1) ~ {exp:.3f}")
    print("    NOTE: pl_z@180d was the project's stated hypothesis before testing (documented");
    print("    in the research log), and the same cell replicates on Coin Metrics and on ETH.")


if __name__ == "__main__":
    part_a()
    part_b()
