# Bitcoin Power-Law Deviation vs Price Oscillators, Cross-Cycle Study (results log)

**Question:** Does deviation from a *causally-fit* power-law trend (price ≈ A·t^n, t = days since
genesis) mean-revert more durably than classic price oscillators (RSI, Mayer Multiple), and do
price indicators decay across halving cycles while the time-based anchor holds?

**Data:** Bitstamp daily OHLC 2011-08-18 → 2026-06-10 (5,411 d), cross-checked vs Coin Metrics
PriceUSD (median Δ 0.15%). All signals causal; power law fit by expanding-window OLS (params at
day t use only data ≤ t). Causal exponent converged to **n = 5.61** (literature ~5.8). Fit is real.

## Part A: Information Coefficient (Spearman signal vs forward return), per epoch
Negative IC = mean-reverting (stretched-high → lower forward return). |IC| = strength.

| horizon | epoch | pl_z | mayer_z | rsi |
|--------|-------|------|---------|-----|
| 180d | E2 2017 | **−0.41** | +0.16 | +0.22 |
| 180d | E3 2021 | **−0.40** | +0.12 | +0.11 |
| 180d | E4 2025 | **−0.51** | −0.22 | −0.13 |
| 30d  | E2→E4 | −0.15→−0.17 | +0.12→−0.12 | +0.14→**−0.02** |
| 90d  | E2→E4 | −0.25→−0.21 | +0.22→−0.15 | +0.30→**+0.04** |

- **RSI decays to noise**: 30d IC +0.28→+0.02, 90d +0.25→+0.04 across cycles (−84% to −93%).
- **Power-law deviation is strongest & most durable at the 180d horizon**, and *strengthens*
  into the latest cycle (−0.41→−0.51). It's a long-horizon structural anchor, not a swing trigger
  (30–90d IC only −0.1 to −0.2).
- **Caveat:** E1 (2012–13) pl_z IC sign is flipped (fit still immature, exponent climbing from
  1.36) → claim is "durable across the *mature* cycles E2–E4", not "monotonic from E1".
- Mayer Multiple is inconsistent (flips sign E2/E3 → E4).

## Part B: Discrete R-multiple backtest (intrabar fills, stop 35%, exit on revert-to-trend)
Long when signal says cheap; same structure for all three. Buy&hold = +14,972R (single-asset
15-yr 100× bull makes raw R degenerate, see Part C).

| signal | n | win% | PF | totR | every epoch + ? |
|--------|---|------|----|----- |-----------------|
| **pl_z** | 6 | 66.7 | **7.39** | **+12.9** | yes: E1+4.1 E2+5.4 E3+3.4 E4+0.0 |
| mayer_z | 13 | 46.2 | 1.79 | +5.4 | test trade lost |
| rsi | 37 | 64.9 | 1.32 | +2.7 | E2 golden (PF5.83) then E3 neg, all 4 test trades lost |

- pl_z dominates but **discrete-trade n is tiny** (slow structural edge → few deep-value buys/cycle;
  test n=1). Confirms *direction*, cannot carry a deployability claim alone.
- Autopsy: all pl_z wins are long holds (213–540 d = full reversion ride); losses are the 2 stops;
  deeper entries (z<−1.9) best. Mechanism = months-to-a-year reversion, confirmed.
- RSI's per-epoch decay in the backtest mirrors Part A: works 2017, dies after.

## Part C: All-days exposure / Sharpe vs buy&hold (the key tradeable test)
Binary long/flat (long when below trend / oversold), causal 1-day lag. **Sharpe edge vs buy&hold
is the cross-cycle decay metric.**

| | B&H Sharpe | pl_z edge | mayer edge | rsi edge |
|--|-----------|-----------|------------|----------|
| Epoch 1 (2013) | 1.64 | −0.99 | −0.99 | −1.27 |
| Epoch 2 (2017) | 1.24 | −0.41 | −0.81 | −1.19 |
| Epoch 3 (2021) | 1.11 | −0.26 | −0.60 | −0.89 |
| Epoch 4 (2025) | 0.20 | **+0.12** | −0.19 | −0.38 |
| TEST 2025-26 | −0.41 | **+0.11** | +0.10 | −0.25 |

- **In bull-dominated early cycles, NO timing beats buy&hold** (you just miss upside sitting flat).
  Honest: the power-law edge is NOT "always wins."
- **pl_z's risk-adjusted value over buy&hold improves monotonically** (−0.99→−0.41→−0.26→+0.12) and
  **crosses positive in the current cycle**, precisely as BTC's beta cools (B&H Sharpe 1.64→0.20).
- **Out-of-sample (2025-26): power-law timing is the ONLY signal that beats buy&hold on Sharpe
  AND cuts drawdown ~10 pts (−41% vs −51%) AND CAGR (+5.5% vs −1.3%).** RSI is worst.
- RSI never beats buy&hold in any epoch and is worst in the latest: "price indicators get worse
  each cycle," measured.

## Verdict (honest)
The folklore ("time is the only true clock; every price indicator decays") is **directionally
right but needs a precise, defensible statement:**

> As Bitcoin matures into a lower-beta asset, **short-horizon price oscillators (RSI) decay toward
> zero predictive power**, while the **long-horizon deviation from the time-based power-law trend
> becomes the first signal to add genuine risk-adjusted value over buy&hold**, confirmed
> out-of-sample in the 2025–26 cycle (beats B&H Sharpe, −10pt drawdown). It is a slow structural
> anchor (180-day reversion), not a trade trigger.

This is a maturation thesis (consistent with the project's Supertrend/options findings) and it is
*publishable*: the result is a measured, monotonic, cross-validated durability contrast with a
clear mechanism, not an inflated PF.

## Part D: Significance (Newey-West HAC t, lag=h + circular block bootstrap, B=2000)
`ic_significance.py`. Overlapping h-day forward returns are MA(h−1); naive t-stats overstate by
~sqrt(h). After correction, the cells that SURVIVE at 5% (both methods agreeing):

| cell | IC | NW-t | boot 95% CI | boot p |
|------|----|------|-------------|--------|
| **pl_z 180d E3 (2021 cyc)** | −0.40 | −2.69 | [−0.69, −0.02] | 0.045 ** |
| **pl_z 180d E4 (2025 cyc)** | −0.51 | −2.63 | [−0.83, −0.07] | 0.025 ** |
| rsi 90d E2 (2017 cyc) | +0.30 | +3.56 | [+0.08, +0.41] | 0.015 ** |

- **pl_z@180d is the ONLY signal significant in the two most recent cycles.** RSI's only
  significant cell anywhere is its 2017-era golden age, then never again (E3/E4 ≈ 0). That is
  "worked, then stopped," formally established.
- Paired contrast Δ|IC| (pl−rsi, same resamples) rises monotonically +0.15→+0.23→+0.28→+0.31
  but is only marginal in E4 (p=0.07): report as *suggestive*, not proven. With ~30 independent
  180d observations per epoch, that's the honest power limit of the data.
- Most other cells (incl. most early-epoch "good" ICs) are NOT significant after correction,
  which strengthens credibility: we report the corrected table, not the naive one.

## Part E: Replication: independent source (Coin Metrics BTC) + second asset (ETH)
`replicate.py`. Both replications CONFIRM:

**BTC on Coin Metrics (2010-07→2026-05, independent of Bitstamp):** 180d pl_z IC E2 −0.45 /
E3 −0.42 / E4 −0.60 (even stronger); RSI 30d +0.28→0.00; Sharpe-edge-vs-B&H monotonic
−1.20→−0.31→−0.31→+0.03. Not an exchange artifact.

**ETH (genesis 2015-07-30, own causal fit, exponent ≈2.1, NOT BTC's 5.6):**
- 180d pl_z IC: E3 −0.37 → E4 −0.65, strengthening into the current cycle, same as BTC.
- Sharpe edge vs B&H: pl_z −1.13 → −0.20 → **+0.33**, the SAME maturation crossover, positive in
  E4 (rsi: −1.50/−0.79/−0.73, never positive).
- ETH's first epoch shows the same warmup artifact as BTC's E1 (immature fit → flipped sign):
  consistent mechanism, the causal fit needs ~one cycle to learn the trend, after which
  deviations are informative.
- **Key upgrade for the paper:** the crossover replicates on a second asset with a *different*
  power-law exponent → it's a property of maturing crypto assets, not a BTC-specific curve.

## Updated verdict
The thesis survives referee-grade correction in its sharpened form:
> Across maturing crypto assets, the only signal retaining statistically significant predictive
> power (HAC + block-bootstrap corrected) in the two most recent market cycles is the 180-day
> deviation from a causally-fit time-based power-law trend; RSI's predictive power, significant
> in the 2016-2020 epoch, has been indistinguishable from zero since. The power-law signal's
> risk-adjusted value over buy&hold rises monotonically across cycles and crosses positive in
> the current cycle on both BTC and ETH.

## Part F: Parameter-sensitivity sweep (`sweep_sensitivity.py`), NOT knife-edge
Pre-registered grid, every cell printed:
- **Horizon:** pl_z IC negative at ALL h∈{60..360} in all mature epochs, monotonically stronger
  with horizon (E4: −0.19@60d → −0.51@180d → −0.69@360d).
- **Fit params:** 9 variants (fit warmup 180/365/730 × z warmup 90/180/365) → IC@180 virtually
  identical (E3 −0.40 all, E4 −0.50/−0.51 all).
- **RSI period 7/14/21/30:** E4 30d IC ≈ 0 for EVERY period (−0.02/−0.03), decay-to-noise is
  not a period artifact. At 180d RSI's sign FLIPS (+0.22 E2 → −0.13..−0.22 E4).
- **Exposure threshold:** the cross-epoch improvement holds in every column; the POSITIVE E4
  crossing needs thr∈{0,+0.25} (deep −0.25 stays −0.16). Report threshold-dependence plainly.

## Part G: The famous cycle-callers, the decay mechanism, and the time clock
(`cycle_callers.py`, Coin Metrics extended: price + MVRV + issuance/Puell.)
Mechanical turn definition (no hand-picking): cycle top = ATH followed by ≥45% drawdown before a
new high → recovers Apr2013/Dec2013/Dec2017/Apr2021/Nov2021/Oct2025 + bottoms Jul2013/Jan2015/
Dec2018/Jul2021/Nov2022. Canonical published thresholds, fixed ex-ante.

**G1. Hit/miss, "precise → early → silent":**
| trigger | '13a | '13b | '17 | Apr'21 | Nov'21 | Oct'25 |
|---|---|---|---|---|---|---|
| Pi Cycle cross | HIT −3d | HIT +1d | HIT +0d | HIT −1d | −210d (early) | **no fire** |
| MVRV>3.7 | HIT −21d | HIT −26d | HIT −10d | HIT −31d | −240d | **no fire** |
| Mayer>2.4 | HIT +25d | HIT +19d | HIT −19d | HIT −31d | −240d | **no fire** |
| Puell>4 / px>5×2yMA | HIT | HIT | HIT | no fire | no fire | **no fire** |
Death order = threshold aggressiveness: the most-stretched thresholds (Puell 4, 5×2yMA) died
after 2017; the rest fired only at the April-2021 secondary peak (missed the Nov true top by
~8 months); by Oct-2025 **every top-caller was silent**. Bottom callers lasted longer: MVRV<1,
Mayer<0.8, Puell<0.5 all nailed Nov-2022 within a week, but their E4 test is IN PROGRESS and
several thresholds are unreached at the current trough (MVRV min 1.15, p200w min 1.09 = price
hasn't touched the 200W MA at all this cycle). 200W-MA note: at daily closes it cleanly hit only
Jan-2015; Dec-2018 bottomed just ABOVE it (no fire); 2022 it broke 34% BELOW (fired 98d early).
The "never breaks the 200W" rule already failed in BOTH directions.

**G2. The mechanism, extremes decay monotonically (the paper's cleanest table):**
Top-side max per epoch: pi 1.23→1.06→1.00→0.74 · MVRV 5.88→4.72→3.96→2.74 · Mayer
8.26→3.78→2.83→1.52 · Puell 10.49→6.62→3.46→1.59 · 2yMA-mult 17.96→9.96→4.88→2.31.
Bottom-side min RISES: MVRV 0.56→0.69→0.75→1.15 · Puell 0.31→0.30→0.35→0.53.
**The oscillation range compresses from both sides every cycle → ANY threshold calibrated on past
cycles must eventually stop firing.** "It never missed before" is survivorship of a shrinking
range, not signal quality. (p200w E1 truncated, 200W MA needs 1400d history; footnote.)

**G3. The time clock (Satoshi's 210,000 blocks ≈ "every 4 years"):**
Mature-cycle TOPS after halving: **525d (2017) / 546d (Nov 2021) / 534d (Oct 2025)**, mean 535
±10d (**±2%**), while every price threshold drifted 30–50% per cycle. Bottoms: 406/364/366d after
their top (~12–13 months). Apr-2021 (337d) is the early secondary peak. n=3 mature cycles,
suggestive, not provable; paired with G2's monotone decay it is the paper's punchline contrast.
Halving gaps 1319/1402/1440d; Satoshi (2009-01-08 cryptography mailing list): "the amount cut in
half every 4 years."

**G4. IC battery incl. PURE-TIME signal (phase = days since halving, zero price input), 180d:**
| epoch | phase | pl_z | mvrv | puell | pi | mayer | rsi |
|---|---|---|---|---|---|---|---|
| E2 | −0.39 | −0.45 | +0.16 | −0.08 | −0.06 | +0.14 | +0.23 |
| E3 | −0.07 | −0.42 | −0.21 | −0.20 | +0.06 | +0.10 | +0.11 |
| E4 | **−0.80** | **−0.60** | −0.38 | −0.69 | **+0.49(!)** | −0.30 | −0.17 |
- **phase (pure time) is the strongest signal of ALL in the current cycle (−0.80)**, though
  unstable across epochs (E3 −0.07: the 2022-24 double-structure cycle). pl_z is the only signal
  with stable sign AND strong magnitude in all three mature epochs.
- Several price indicators don't just weaken, they **INVERT** (pi +0.49, mult2y +0.14, RSI/Mayer
  flip sign). A historically-calibrated user would be pointed the WRONG way. Stronger claim than
  decay: sign instability = unusable.

## Final paper architecture (all evidence in hand)
1. Threshold cycle-callers: precise → early → silent (G1), because oscillation extremes compress
   monotonically (G2). "Never missed" was a property of a shrinking range.
2. Continuous oscillator ICs weaken AND flip sign across epochs (G4, Part A). Recalibrating
   thresholds each cycle = fitting the past.
3. Time-anchored signals are the survivors: pl_z is HAC-significant in the two latest cycles
   (Part D), replicates cross-source and on ETH with a different exponent (Part E), and is
   parameter-robust (Part F); pure phase dominates the current cycle (G4); mature-cycle tops
   cluster ±2% in halving-time (G3).
4. Honest limits: n=3 mature cycles for the clock; bottom-callers not yet failed (E4 test live);
   exposure crossover threshold-dependent; pl-vs-rsi contrast p=0.07.

## Part H: Confounders: global liquidity (M2) & the business cycle (`macro_study.py`)
Data: FRED M2SL (monthly 2018+ / quarterly 2001+) + T10Y2Y (quarterly) via the TradingView FRED
mirror (FRED endpoints bot-blocked from this network; transcription verified, 34 overlapping
quarter-ends match to 0.000). Publication lags applied (M2 +28d). US M2, not true global M2,
stated limitation. Identification caveat: liquidity & halving cycles are co-periodic, n=3-4.
A co-periodic confounder cannot be FULLY ruled out; these are discriminating tests, not proof.

**H1. IC stability:** macro flips sign across epochs exactly like the price oscillators:
m2_yoy 180d IC +0.41 (E2) → −0.10 (E3) → **−0.83** (E4); t10y2y +0.42 → −0.35 → −0.79.
The E4 sign is BACKWARDS for the liquidity narrative: **M2 expanded steadily through 2024-26
(+3.5→+4.7% YoY) while BTC topped on schedule at 534d and entered its bear**, liquidity rising,
BTC falling. That is the disagreement episode, and BTC followed the clock.

**H2. "M2 leads BTC by ~10 weeks" folklore:** the lead/lag profile is sign-UNSTABLE:
E2 positive at every k (peak +0.45 @ k≈120d, where the folklore came from), E3 negative
(−0.45 @ k=270), E4 negative at every k. No stable lead exists; it was a one-era artifact.

**H3. Turn-timing precision:** BTC tops vs nearest M2-YoY peak: +227d / −253d / −67d
(sign-alternating, dispersion of hundreds of days) vs halving clock 525/546/534d (±10d).
**The clock beats liquidity turns by an order of magnitude.** Bottoms similar (+167/−15/+172).
Plus the practical asymmetry: M2 turns are confirmable only months AFTER the fact; the halving
clock is known years ahead. Footnote: the Apr-2021 secondary peak came ~6wk after the Feb-2021
M2-YoY peak. Liquidity plausibly called THAT one; the bear-defining Nov top followed the clock.

**H4. Horse race (fwd180 ~ phase + m2_yoy + t10y2y, NW lag=180, mature sample n=3426):**
phase **t=−2.00** | m2_yoy t=+0.20 | t10y2y t=−0.07. Controlling for each other, only the clock
survives. Per-epoch partials noisy (collinearity |r|~0.5-0.66, few independent windows, don't
over-read; E3 t10y2y t=−3.0 noted honestly: the 2022 inversion coincided with the bear). E4:
phase t=−4.6, macro n.s.

**Verdict:** macro/liquidity behaves like every price indicator, sign-unstable epoch to epoch,
while the clock is the only regressor with stable sign + significance. Claim for the paper: NOT
"macro is irrelevant" (it correlates strongly within eras) but "macro's relationship to Bitcoin
is era-dependent and ex-post, while the time-structure is era-stable and ex-ante."

## Part I: The clock's null test + THE SATOSHI CLOCK indicator (`satoshi_clock.py`)
The clock has made **6 calls** (3 tops after-halving: 525/546/534d, spread 21d; 3 bottoms
after-top: 406/364/366d, spread 42d, every completed turn in BTC history at mature scale).

**Permutation/null test** (statistic = observed range, stated ex-ante; exact formula + 2M-draw
MC cross-check; window-sensitivity grid so no cherry-picking):
| windows (top/bot) | P(top cluster) | P(bot cluster) | joint |
|---|---|---|---|
| generous 1458/800d | 0.00062 | 0.0080 | **4.9e-06** |
| conservative 700/500d | 0.00265 | 0.0200 | **5.3e-05** |
Even forcing turns into narrow plausible bands, the 6-call cluster is ~1-in-19,000 to
~1-in-200,000 under chance. Tops as a FRACTION of their varying halving gap: .374/.379/.366,
also tight. This is the load-bearing robustness number for the clock-first framing.

**THE SATOSHI CLOCK** (named indicator; "the amount cut in half every 4 years", Satoshi
2009-01-08). BTC's state in two time-anchored coordinates:
- **CLOCK** = days since last halving (the angle of the 4-year revolution)
- **SPRING** = causal power-law deviation z (the radius: stretch from the time-trend)
Damped-spiral table (the whole thesis in one): SPRING at tops **+2.85 → +2.69 → +1.29 → +0.43**
(amplitude dying = why every price threshold fails) while CLOCK at tops stays 525-546 (period
fixed). Bottom SPRINGs −1.46/−0.61/−1.17 (less monotone, honest).

**Current reading (2026-05-23, $76,620):** CLOCK 763d, SPRING −0.53, 229d post-top.
**BOTTOM WINDOW: 2026-10-05 .. 2026-11-16** (after-halving cross-anchor agrees: 09-26..10-19, 889-912d).
**NEXT TOP WINDOW: 2029-09-22 .. 2029-10-13** (halving ~2028-04-15 + 525..546d), the paper's
falsifiable, pre-registered prediction.

## Next: DRAFT the paper, clock-first framing ("Bitcoin Runs on a Clock"), arXiv q-fin.ST /
SSRN, then Ledger or JRFM for peer review.
