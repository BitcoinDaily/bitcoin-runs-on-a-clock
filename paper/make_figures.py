"""
make_figures.py — generates the 7 manuscript figures (Appendix B) into paper/figures/.
Run from PowerLaw/: python paper/make_figures.py
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pl_lib
import cycle_callers as cc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
})
EP_COLOR = {1: "#9e9e9e", 2: "#1f77b4", 3: "#2ca02c", 4: "#d62728"}
EP_NAME = {1: "Epoch 1 (2013 cycle)", 2: "Epoch 2 (2017)", 3: "Epoch 3 (2021)",
           4: "Epoch 4 (2025)"}
H = pl_lib.HALVINGS
GAPS = {1: 1319, 2: 1402, 3: 1440, 4: 1458}
TURNS = [("top", "2013-12-04"), ("bot", "2015-01-14"), ("top", "2017-12-16"),
         ("bot", "2018-12-15"), ("top", "2021-11-08"), ("bot", "2022-11-09"),
         ("top", "2025-10-06")]


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p)
    plt.close(fig)
    print(f"  saved {name}")


# ----------------------------------------------------------------- Fig 1: power law
def fig1():
    df = pl_lib.build_signals(pl_lib.load_prices())  # Bitstamp
    fig, (a, b) = plt.subplots(2, 1, figsize=(7, 6.5), height_ratios=[3, 1],
                               sharex=False, layout="constrained")
    t = df["t"].to_numpy(); c = df["c"].to_numpy()
    a.plot(t, c, lw=0.6, color="#444", label="BTC daily close (Bitstamp)")
    # trend_t = exp(lnA_t + n_t ln t) == c / exp(resid)
    trend = df["c"].to_numpy() / np.exp(df["pl_resid"].to_numpy())
    a.plot(t, trend, lw=1.6, color="#d62728",
           label="causal power-law trend  $A_t\\,t^{\\,n_t}$ (expanding fit)")
    a.set_xscale("log"); a.set_yscale("log")
    a.set_ylabel("price, USD (log)")
    a.set_title("Bitcoin price vs time since genesis: causally fit power law")
    a.legend(frameon=False, loc="upper left")
    b.plot(t, df["pl_n"], lw=1.2, color="#1f77b4")
    b.axhline(5.61, color="#d62728", lw=0.8, ls="--")
    b.text(t[-1], 5.61, "  5.61", color="#d62728", va="center")
    b.set_xscale("log"); b.set_ylim(0, 13)
    b.set_xlabel("days since genesis (log)"); b.set_ylabel("exponent $n_t$")
    b.set_title("Convergence of the causally-estimated exponent")
    save(fig, "fig1_powerlaw.png")


# --------------------------------------------------------- Fig 2: the damped spiral
def fig2(df):
    # NO floating text inside the plot (it always collides because the tops cluster in one wedge).
    # Everything is carried by the visuals + the title block + the caption below the figure.
    fig = plt.figure(figsize=(7.6, 8.4))
    ax = fig.add_subplot(111, projection="polar")
    R0 = 2.5
    gm = np.mean([GAPS[2], GAPS[3], GAPS[4]])

    for e in [1, 2, 3, 4]:
        sub = df[(df["epoch"] == e)].dropna(subset=["pl_z"])
        if not len(sub):
            continue
        ph = (sub.index - H[e]).days.to_numpy()
        theta = 2 * np.pi * ph / GAPS[e]
        r = pd.Series(sub["pl_z"].to_numpy()).rolling(31, min_periods=5).mean() + R0
        ax.plot(theta, r, lw=2.4, color=EP_COLOR[e], label=EP_NAME[e], alpha=0.8,
                solid_capstyle="round", zorder=3)

    # the top-window wedge (shaded only, no label)
    wedge_th = np.linspace(2 * np.pi * 525 / gm, 2 * np.pi * 546 / gm, 40)
    ax.fill_between(wedge_th, 0, R0 + 3.6, color="#d62728", alpha=0.18, zorder=1)

    # markers only; collect mature tops for the inward arrow
    mature = []
    for kind, d in TURNS:
        t = pd.Timestamp(d)
        e = int(pl_lib.epoch_of(pd.DatetimeIndex([t]))[0])
        ph = (t - H[e]).days
        z = df["pl_z"].iloc[df.index.get_indexer([t], method="nearest")[0]]
        th = 2 * np.pi * ph / GAPS[e]
        if kind == "top":
            ax.plot([th], [z + R0], "^", ms=15, color=EP_COLOR[e], zorder=6, mec="black", mew=1.4)
            if ph >= 450:
                mature.append((th, z + R0))
        else:
            ax.plot([th], [z + R0], "v", ms=7, color="#bdbdbd", zorder=4, mec="white", mew=0.7)

    # inward dashed arrow through the mature tops (visual only): amplitude dying on a fixed angle
    mature.sort(key=lambda p: p[1], reverse=True)
    th_arr = [p[0] for p in mature]; r_arr = [p[1] for p in mature]
    ax.plot(th_arr, r_arr, color="black", lw=2.6, ls=(0, (5, 2)), zorder=5, solid_capstyle="round")
    ax.annotate("", (th_arr[-1], r_arr[-1]), (th_arr[-2], r_arr[-2]),
                arrowprops=dict(arrowstyle="-|>", lw=2.6, color="black"), zorder=7)

    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    ticks_d = [0, 182, 365, 730, 912, 1095, 1277]
    ax.set_xticks([2 * np.pi * d / gm for d in ticks_d])
    ax.set_xticklabels([f"{d}d" for d in ticks_d], fontsize=10)
    ax.set_yticks([R0 - 1, R0, R0 + 1, R0 + 2, R0 + 3])
    ax.set_yticklabels(["z=-1", "z=0", "z=+1", "z=+2", "z=+3"], fontsize=7.5, color="#9a9a9a")
    ax.set_rlabel_position(168)
    ax.set_ylim(0, R0 + 3.8)
    ax.grid(alpha=0.3)

    # exactly two labels, both anchored on the empty right margin with leader lines into the SE
    thw = 2 * np.pi * 535 / gm
    ax.annotate("TOP WINDOW\n525–546 days", xy=(thw, R0 + 3.5), xytext=(1.07, 0.20),
                textcoords="axes fraction", ha="left", va="center", fontsize=11,
                fontweight="bold", color="#b00000", annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color="#b00000", lw=1.4))
    ax.annotate("amplitude dying:\ntops spiral inward", xy=(thw, (r_arr[0] + r_arr[-1]) / 2),
                xytext=(1.07, 0.46), textcoords="axes fraction", ha="left", va="center",
                fontsize=11, fontweight="bold", color="black", annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color="black", lw=1.4))

    ax.set_title("The Satoshi Clock: a damped spiral\n"
                 "angle = days since halving (CLOCK),   radius = power-law deviation (SPRING)",
                 pad=20, fontsize=12.5, fontweight="bold")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False,
              fontsize=9, columnspacing=1.2, handletextpad=0.4)
    save(fig, "fig2_satoshi_clock_spiral.png")


# ------------------------------------------------ Fig 3: extremes compression funnel
def fig3(df):
    tops = {"Pi ratio": "pi", "MVRV": "mvrv", "Mayer": "mayer", "Puell": "puell",
            "2yr-MA mult": "mult2y"}
    bots = {"MVRV": "mvrv", "Mayer": "mayer", "Puell": "puell"}
    fig, (a, b) = plt.subplots(1, 2, figsize=(8.6, 3.6))
    xs = [1, 2, 3, 4]
    for name, col in tops.items():
        vals = [df[df["epoch"] == e][col].max() for e in xs]
        a.plot(xs, np.array(vals) / vals[0], "-o", ms=4, label=name)
    a.set_yscale("log")
    a.set_xticks(xs); a.set_xticklabels(["E1", "E2", "E3", "E4"])
    a.set_ylabel("cycle MAX, relative to Epoch 1 (log)")
    a.set_title("Top-side extremes compress every cycle")
    a.legend(frameon=False, fontsize=8)
    for name, col in bots.items():
        vals = [df[df["epoch"] == e][col].min() for e in xs]
        b.plot(xs, vals, "-o", ms=4, label=name)
    b.set_xticks(xs); b.set_xticklabels(["E1", "E2", "E3", "E4"])
    b.set_ylabel("cycle MIN (level)")
    b.set_title("Bottom-side extremes end the era higher (path not monotone)")
    b.legend(frameon=False, fontsize=8)
    fig.suptitle("The mechanism: top-side extremes compress monotonically and bottom-side minima end higher,\n"
                 "so any fixed threshold must eventually stop firing", y=1.06, fontsize=9.5)
    save(fig, "fig3_extremes_funnel.png")


# ------------------------------------------------------------- Fig 4: IC decay bars
def fig4(df):
    from study_signals import fwd_return, spearman
    for h in [30, 180]:
        df[f"fwd{h}"] = fwd_return(df["c"].to_numpy(), h)
    sigs = ["phase", "pl_z", "mvrv", "puell", "mayer", "rsi"]
    labels = ["phase\n(time)", "pl_z\n(trend)", "MVRV", "Puell", "Mayer", "RSI-14"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
    for ax, h in zip(axes, [30, 180]):
        w = 0.25
        for j, e in enumerate([2, 3, 4]):
            sub = df[df["epoch"] == e]
            ics = []
            for s in sigs:
                d2 = sub.dropna(subset=[s, f"fwd{h}"])
                ics.append(spearman(d2[s], d2[f"fwd{h}"]) if len(d2) >= 60 else np.nan)
            ax.bar(np.arange(len(sigs)) + (j - 1) * w, ics, width=w,
                   color=EP_COLOR[e + 0], label=EP_NAME[e], alpha=0.9)
        ax.axhline(0, color="#333", lw=0.7)
        ax.set_xticks(range(len(sigs))); ax.set_xticklabels(labels, fontsize=7.5)
        ax.set_title(f"forward {h}-day return")
    axes[0].set_ylabel("Spearman IC")
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Information coefficients per epoch: price/on-chain signals decay and flip "
                 "sign; the time-anchored signals do not", y=1.04, fontsize=9.5)
    save(fig, "fig4_ic_decay.png")


# --------------------------------------------- Fig 5: cycle-caller firings timeline
def fig5(df):
    tops, bottoms, _ = cc.cycle_turns(df)
    fig, (a, b) = plt.subplots(2, 1, figsize=(8.6, 5.6), height_ratios=[2, 2],
                               sharex=True)
    a.plot(df.index, df["c"], lw=0.7, color="#444")
    a.set_yscale("log"); a.set_ylabel("BTC, USD (log)")
    for t in tops:
        if t.year > 2011:
            a.axvline(t, color="#d62728", lw=0.8, ls="--", alpha=0.8)
    for bt in bottoms:
        if bt.year > 2011:
            a.axvline(bt, color="#1f77b4", lw=0.8, ls=":", alpha=0.8)
    a.set_title("Cycle turns (red dashed = tops, blue dotted = bottoms) and "
                "every canonical indicator firing")
    trig = list(cc.TOP_TRIGGERS.items()) + list(cc.BOT_TRIGGERS.items())
    for i, (name, cond) in enumerate(trig):
        fs = [f for f in cc.fires(cond(df)) if f.year > 2011]
        y = len(trig) - i
        b.scatter(fs, [y] * len(fs), s=14,
                  color="#d62728" if i < len(cc.TOP_TRIGGERS) else "#1f77b4", zorder=3)
        b.text(df.index[0], y, name + "  ", ha="right", va="center", fontsize=7.5)
    for t in tops:
        if t.year > 2011:
            b.axvline(t, color="#d62728", lw=0.8, ls="--", alpha=0.5)
    for bt in bottoms:
        if bt.year > 2011:
            b.axvline(bt, color="#1f77b4", lw=0.8, ls=":", alpha=0.5)
    b.set_yticks([]); b.set_xlim(df.index[0], df.index[-1])
    b.set_title("Top-caller hits (red) collectively cover every top through Apr-2021; all silent at the "
                "2025 top; bottom-callers (blue) still fired in 2022", fontsize=9)
    save(fig, "fig5_caller_timeline.png")


# ------------------------------------------- Fig 6: the maturation Sharpe crossover
def fig6():
    # Sharpe edge vs buy&hold per epoch (computed in exposure_study.py / replicate.py)
    series = {
        "BTC pl_z (Bitstamp)": ([1, 2, 3, 4], [-0.99, -0.41, -0.26, +0.12], "#d62728", "-o"),
        "BTC pl_z (Coin Metrics)": ([1, 2, 3, 4], [-1.20, -0.31, -0.31, +0.03], "#ff9896", "-s"),
        "ETH pl_z": ([2, 3, 4], [-1.13, -0.20, +0.33], "#9467bd", "-^"),
        "BTC RSI (Bitstamp)": ([1, 2, 3, 4], [-1.27, -1.19, -0.89, -0.38], "#7f7f7f", "--o"),
    }
    fig, ax = plt.subplots(figsize=(6.4, 4))
    for name, (xs, ys, col, st) in series.items():
        ax.plot(xs, ys, st, color=col, label=name, ms=5)
    ax.axhline(0, color="#333", lw=0.8)
    ax.fill_between([0.8, 4.2], 0, 0.45, color="#2ca02c", alpha=0.06)
    ax.text(1.0, 0.38, "timing adds value over buy & hold", fontsize=8, color="#2ca02c")
    ax.set_xticks([1, 2, 3, 4]); ax.set_xticklabels(["E1\n2013", "E2\n2017", "E3\n2021",
                                                     "E4\n2025"])
    ax.set_xlim(0.8, 4.2)
    ax.set_ylabel("Sharpe edge vs buy & hold")
    ax.set_title("The maturation crossover: time-trend timing crosses positive in the "
                 "current cycle, on both assets")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    save(fig, "fig6_maturation_crossover.png")


# ---------------------------------------------------- Fig 7: M2 vs the halving clock
def fig7():
    m2 = pd.read_csv("macro_m2.csv", parse_dates=["date"]).set_index("date")["M2SL"]
    yoy = (m2 / m2.shift(freq="365D").reindex(m2.index, method="nearest")) - 1
    from macro_study import local_turns
    pk, tr = local_turns(yoy)
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    ax.plot(yoy.index, yoy * 100, lw=1.2, color="#1f77b4", label="US M2 growth, YoY %")
    for p in pk:
        if p.year >= 2012:
            ax.axvline(p, color="#1f77b4", lw=0.7, ls="--", alpha=0.6)
    btc_tops = ["2017-12-16", "2021-11-08", "2025-10-06"]
    offs = ["+227d", "-253d", "-67d"]
    for d, o in zip(btc_tops, offs):
        t = pd.Timestamp(d)
        ax.axvline(t, color="#d62728", lw=1.2)
        ax.text(t, ax.get_ylim()[1] * 0.92 if False else 24, f" BTC top\n {d[:7]}\n nearest M2 "
                f"peak {o}", fontsize=7, color="#d62728", va="top")
    ax.axhline(0, color="#333", lw=0.6)
    ax.set_ylabel("M2 YoY, %")
    ax.set_xlim(pd.Timestamp("2012-01-01"), yoy.index[-1])
    ax.set_title("Liquidity turns (blue dashed = M2-YoY peaks) miss Bitcoin tops (red) by "
                 "67-253 days, mixed in sign;\nthe halving clock holds them to ±10d",
                 fontsize=9.5)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    save(fig, "fig7_m2_vs_clock.png")


if __name__ == "__main__":
    print("generating figures ->", OUT)
    fig1()
    dfc = cc.build()
    fig2(dfc)
    fig3(dfc)
    fig4(dfc)
    fig5(dfc)
    fig6()
    fig7()
    print("done.")
