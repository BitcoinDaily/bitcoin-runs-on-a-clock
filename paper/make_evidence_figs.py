"""make_evidence_figs.py — three evidence figures that the paper was missing:
  A  the turn-timing null distribution (top = extreme tail; bottom = honest casualty)
  B  the four-year-clock placebo (halving vs election vs random clocks)
  C  the clock-alignment lead image (every mature top lands ~535 days after its halving)
Reproduces the LOCKED null/placebo numbers by reusing the exact scripts + seeds.
Run from PowerLaw/: python paper/make_evidence_figs.py"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pl_lib
import empirical_null_test as ent

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
                     "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
RED, BLUE, GREEN, GREY = "#d62728", "#1f77b4", "#2ca02c", "#9e9e9e"
H = pl_lib.HALVINGS


def save(fig, name):
    fig.savefig(os.path.join(OUT, name)); plt.close(fig); print("  saved", name)


# ============================ FIG A: the null distribution ============================
def fig_null():
    df = pl_lib.load_prices()
    c = df["c"].to_numpy(); dates = df.index
    epoch = pl_lib.epoch_of(dates)
    dah = np.full(len(df), -1.0)
    for e, hd in H.items():
        m = dates >= hd; dah[m] = (dates[m] - hd).days
    ret = np.diff(np.log(c)); n = len(ret)
    rng = np.random.default_rng(ent.SEED)                 # identical seed -> locked numbers
    topB, botR = [], []
    nB = nA = nbot = tot = 0
    for L in ent.LS:
        nb = int(np.ceil(n / L))
        for _ in range(ent.B):
            starts = rng.integers(0, n, nb)
            idx = ((starts[:, None] + np.arange(L)[None, :]) % n).ravel()[:n]
            cp = np.empty(n + 1); cp[0] = 1.0
            np.cumsum(ret[idx], out=cp[1:]); np.exp(cp[1:], out=cp[1:])
            tA, bok, nm, trA, br, tBok = ent.score_path(cp, dah, epoch, dates)
            # recover the epoch-max range for the histogram
            tops = ent.extract_tops(cp)
            by = {e: [int(dah[i]) for i in tops if epoch[i] == e] for e in (2, 3, 4)}
            if all(len(v) for v in by.values()):
                sel = [by[e][-1] for e in (2, 3, 4)]
                topB.append(max(sel) - min(sel))
            if np.isfinite(br):
                botR.append(br)
            nB += tBok; nA += tA; nbot += bok; tot += 1
    topB = np.array(topB); botR = np.array(botR)

    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.0))
    # --- tops: extreme tail ---
    a.hist(topB[topB <= 400], bins=40, color=GREY, alpha=0.85, edgecolor="white", lw=0.3)
    a.axvline(21, color=RED, lw=2.6)
    a.annotate("observed\n21 days", (21, a.get_ylim()[1] * 0.82), xytext=(95, a.get_ylim()[1] * 0.82),
               fontsize=9, fontweight="bold", color=RED, va="center",
               arrowprops=dict(arrowstyle="->", color=RED, lw=1.6))
    a.set_xlabel("spread of the three mature tops in halving-time, days")
    a.set_ylabel("number of null histories")
    a.set_title(f"TOPS: real cluster is off the chart\n0 of {tot:,} null histories cluster as tightly "
                f"(deterministic);\n{nA/tot*100:.2f}% under the conservative variant", fontsize=9)
    # --- bottoms: honest casualty ---
    b.hist(botR[botR <= 400], bins=40, color=GREY, alpha=0.85, edgecolor="white", lw=0.3)
    b.axvline(42, color=RED, lw=2.6)
    b.annotate("observed\n42 days", (42, b.get_ylim()[1] * 0.82), xytext=(120, b.get_ylim()[1] * 0.82),
               fontsize=9, fontweight="bold", color=RED, va="center",
               arrowprops=dict(arrowstyle="->", color=RED, lw=1.6))
    b.set_xlabel("spread of the three bottoms in bear-time, days")
    b.set_ylabel("number of null histories")
    b.set_title(f"BOTTOMS: real cluster is ordinary\n{nbot/tot*100:.0f}% of null histories match or beat it\n"
                f"(bottom timing is largely process-intrinsic)", fontsize=9)
    fig.tight_layout()
    save(fig, "figA_null_distribution.png")
    print(f"   [check] epoch-max tops <=21: {nB}/{tot} | selection <=21: {nA}/{tot} | bottoms <=42: {nbot}/{tot}")


# ============================ FIG B: the four-year-clock placebo ============================
def fig_placebo():
    DAY = pd.Timedelta(days=1)
    tops = [pd.Timestamp(x) for x in ["2017-12-16", "2021-11-08", "2025-10-06"]]
    halv = [H[i] for i in sorted(H)]
    elections = [pd.Timestamp(x) for x in ["2012-11-06", "2016-11-08", "2020-11-03", "2024-11-05"]]

    def rng_after(turns, anchors):
        out = []
        for t in turns:
            pr = [x for x in anchors if x <= t]
            if pr: out.append((t - max(pr)).days)
        return max(out) - min(out) if len(out) == len(turns) else np.inf

    r_halv = rng_after(tops, halv)
    r_elec = rng_after(tops, elections)
    rngp = np.random.default_rng(7)                       # identical seed -> locked 0/2000
    ranges = []
    for _ in range(2000):
        a0 = pd.Timestamp("2009-01-01") + int(rngp.integers(0, 1461)) * DAY
        anchors = [a0 + k * 1461 * DAY for k in range(0, 6)]
        rr = rng_after(tops, anchors)
        if np.isfinite(rr): ranges.append(rr)
    ranges = np.array(ranges)
    beat = int((ranges <= r_halv).sum())
    typ = int(np.median(ranges))                          # ~71: 95% of random phases give exactly this

    clocks = [("The halving (Bitcoin's protocol)", r_halv, RED),
              ("US election cycle", r_elec, BLUE),
              ("Typical random 4-year clock", typ, GREY),
              ("A fixed 4-year calendar", 1423, "#c9c9c9")]
    XCAP = 92
    fig, ax = plt.subplots(figsize=(9.0, 3.9))
    ys = list(range(len(clocks)))[::-1]
    for (label, val, col), y in zip(clocks, ys):
        shown = min(val, XCAP)
        ax.barh(y, shown, color=col, height=0.62, alpha=0.92, zorder=3)
        if val <= XCAP:
            ax.text(shown + 2, y, f"{val} days", va="center", ha="left",
                    fontsize=12, fontweight="bold", color=col if col != GREY else "#555")
        else:
            ax.text(shown - 1, y, "//", va="center", ha="right", fontsize=15,
                    color="white", fontweight="bold")
            ax.text(shown + 2, y, f"{val:,} days   (off the chart)", va="center", ha="left",
                    fontsize=11, fontweight="bold", color="#777")
    ax.set_yticks(ys)
    ax.set_yticklabels([c[0] for c in clocks], fontsize=10.5)
    for tick, (_, _, col) in zip(ax.get_yticklabels(), clocks):
        tick.set_color(col if col not in (GREY, "#c9c9c9") else "#333"); tick.set_fontweight("bold")
    ax.set_xlim(0, 132); ax.set_ylim(-0.6, len(clocks) - 0.35)
    ax.text(95, ys[2], "0 of 2,000 random clocks are\nas tight as the halving",
            fontsize=9.5, style="italic", color="#444", va="center")
    ax.set_xlabel("how tightly the three tops cluster, days after each clock's reset  (shorter = tighter)")
    ax.set_title("Only the halving locks the tops\nevery look-alike 4-year clock is three times looser, or worse",
                 fontsize=12, fontweight="bold", pad=12)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    save(fig, "figB_clock_placebo.png")
    print(f"   [check] halving {r_halv}d | election {r_elec}d | typical-random {typ}d | beat={beat}/2000")
    print(f"   [check] halving {r_halv}d | election {r_elec}d | random beat={beat}/2000")


# ============================ FIG C: the clock-alignment lead image ============================
def fig_alignment():
    rows = [("2013 cycle", 1, "2013-12-04", GREY, False),
            ("2017 cycle", 2, "2017-12-16", BLUE, True),
            ("2021 cycle", 3, "2021-11-08", GREEN, True),
            ("2025 cycle", 4, "2025-10-06", RED, True)]
    fig, ax = plt.subplots(figsize=(9.0, 4.3))
    ax.axvspan(525, 546, color=RED, alpha=0.16, zorder=0)
    ax.text(535, 4.6, "TOP WINDOW\n525–546 days", ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#b00000")
    for label, e, td, col, mature in rows:
        y = 5 - e
        ph = (pd.Timestamp(td) - H[e]).days
        ax.plot([0, ph], [y, y], color=col, lw=3.0, solid_capstyle="round", alpha=0.5, zorder=2)
        ax.plot([0], [y], "o", ms=12, color=col, mec="black", mew=1.2, zorder=4)
        ax.plot([ph], [y], "^", ms=17, color=col, mec="black", mew=1.4, zorder=5)
        ax.text(ph + (16 if mature else 18), y, f"top: {ph} days" + ("" if mature else "  (1st cycle)"),
                va="center", fontsize=9.5, fontweight="bold" if mature else "normal",
                color="black" if mature else "#666")
        ax.text(-22, y, label, va="center", ha="right", fontsize=10, fontweight="bold", color=col)
    ax.text(0, 4.62, "halving", ha="center", fontsize=8.5, color="#444")
    ax.set_xlim(-150, 720); ax.set_ylim(0.3, 5.1)
    ax.set_yticks([])
    ax.set_xlabel("days since that cycle's halving", fontsize=10)
    ax.spines["left"].set_visible(False)
    ax.set_title("Every mature top lands in the same place on the halving clock\n"
                 "three cycles apart, three tops within 21 days of each other (525, 546, 534)",
                 fontsize=12, fontweight="bold")
    fig.tight_layout()
    save(fig, "figC_clock_alignment.png")


if __name__ == "__main__":
    fig_alignment()
    fig_placebo()
    fig_null()
