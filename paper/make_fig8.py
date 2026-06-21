"""make_fig8.py — Figure 8: the clock governs the whole cycle, not just the turns.
Left: each cycle's price path aligned by days-since-halving (they rhyme). Right: average
forward-90d return by phase (boom -> bust at the top window -> recovery). Run from PowerLaw/."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pl_lib

plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
                     "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
EP_COLOR = {1: "#9e9e9e", 2: "#1f77b4", 3: "#2ca02c", 4: "#d62728"}
EP_NAME = {1: "2013 cycle", 2: "2017 cycle", 3: "2021 cycle", 4: "2025 cycle"}
H = pl_lib.HALVINGS

df = pl_lib.load_prices()
lp = np.log(df["c"])
fig, (a, b) = plt.subplots(1, 2, figsize=(9.5, 3.8))

# ---- left: phase-aligned price paths ----
for e in [1, 2, 3, 4]:
    h = H[e]
    nxt = H.get(e + 1)
    m = (df.index >= h) & ((df.index < nxt) if nxt is not None else True)
    sub = lp[m]
    d = (sub.index - h).days
    a.plot(d, sub.values - sub.values[0], color=EP_COLOR[e], lw=1.3, label=EP_NAME[e], alpha=0.9)
a.axvspan(525, 546, color="#d62728", alpha=0.12)
a.text(535, a.get_ylim()[1] * 0.92, "top\nwindow", color="#d62728", fontsize=7, ha="center")
a.set_xlim(0, 1300)
a.set_xlabel("days since halving"); a.set_ylabel("log price, normalized to halving day")
a.set_title("Every cycle traces the same shape in halving-time\n(cross-cycle correlation 0.72; random alignment 0.02)", fontsize=9)
a.legend(frameon=False, fontsize=7.5, loc="upper left")

# ---- right: return-by-phase ----
c = df["c"]; fwd = (c.shift(-90) / c - 1.0).to_numpy()
dsh = np.full(len(df), np.nan)
for e, h in H.items():
    mm = df.index >= h
    dsh[mm] = (df.index[mm] - h).days
ok = (~np.isnan(dsh)) & (~np.isnan(fwd)) & (dsh < 1300)
d2, f2 = dsh[ok], fwd[ok]
edges = np.arange(0, 1301, 130)
cent = (edges[:-1] + edges[1:]) / 2
means = [f2[(d2 >= edges[i]) & (d2 < edges[i + 1])].mean() if ((d2 >= edges[i]) & (d2 < edges[i + 1])).sum() > 20 else np.nan
         for i in range(len(edges) - 1)]
cols = ["#2ca02c" if (m or 0) > 0 else "#d62728" for m in means]
b.bar(cent, [m * 100 if m is not None else 0 for m in means], width=110, color=cols, alpha=0.85)
b.axhline(0, color="#333", lw=0.8)
b.axvspan(525, 546, color="#d62728", alpha=0.18)
b.text(535, b.get_ylim()[1] * 0.8, "top\nwindow", color="#7a0000", fontsize=7, ha="center")
b.set_xlim(0, 1300)
b.set_xlabel("days since halving"); b.set_ylabel("avg forward 90-day return, %")
b.set_title("Returns flip positive->negative at the top window,\nand back to positive near the bottom", fontsize=9)

fig.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "fig8_cycle_shape.png")
fig.savefig(out, bbox_inches="tight"); print("saved", out)
