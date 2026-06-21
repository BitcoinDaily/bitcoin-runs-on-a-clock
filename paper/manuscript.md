# Bitcoin Runs on a Clock: Why Every Price Indicator Dies and the Halving Clock Doesn't

**Josh Molnar**
*Independent Researcher*
*June 2026*

---

## Abstract

Every widely followed Bitcoin cycle indicator (the Pi Cycle Top, MVRV, the Mayer Multiple, the Puell Multiple, the 200-week moving average) called the market's tops and bottoms with striking precision for a decade, then degraded in a common sequence: precise, then early, then silent. We show that this is not a series of independent failures but a single structural phenomenon. Using daily data spanning the four halving epochs (2011–2026; the fourth is still in progress), we document three things. First, the per-cycle maxima of the five major top-calling oscillators decline monotonically across all four epochs while their per-cycle minima end the era higher than they began, so any threshold calibrated on past cycles must eventually stop firing. Second, the predictive power of short-horizon price indicators decays toward zero across epochs and in several cases inverts sign. Third, Bitcoin's *time* structure remains fixed: the three mature-cycle tops occurred 525, 546, and 534 days after their respective halvings, and the three completed bear-market bottoms 406, 364, and 366 days after their tops.

These turns are identified retrospectively by a fixed mechanical rule (an all-time high followed by a ≥45% drawdown), not from a real-time forecasting record. Under uniform timing-free nulls, the joint probability of both clusters ranges from 5×10⁻⁶ to 1×10⁻³ across every window choice and inclusion variant we examine, including the variant least favorable to the claim. A harder empirical null, in which block-bootstrapped Bitcoin return paths are processed by the identical turn rule, never reproduces the top-timing regularity under its deterministic construction (zero of 10,000 paths across five block lengths; a conservative variant that grants the null free selection among candidate tops yields 0.10–0.25%). The same null reveals that the *bottom*-timing regularity is largely intrinsic to the drawdown process itself, reproduced by 31–43% of null paths: the clock evidence is concentrated in the tops' halving-phase alignment, and we weight our predictions accordingly. A causally fit power law in time-since-genesis (exponent converging to 5.6) is the only signal in the formal inference battery whose direction is stable across every mature epoch, whose long-horizon relationship replicates on an independent price source and on Ethereum with a different exponent, and whose risk-adjusted timing edge over buy-and-hold improves monotonically across all four cycles, turning positive in the current one (a single-window holdout, suggestive rather than decisive). We deliberately rest none of this on per-epoch significance testing: a dependence-preserving rotation null shows that autocorrelation-robust (HAC) inference over-rejects severely for persistent signals at these sample sizes (empirical size up to 0.33 at nominal 0.05), rendering the apparent two-epoch significance of the power-law cell statistically indistinguishable from chance (empirical p = 0.21). We report this diagnostic in full, because it disqualifies not only our own per-epoch p-values but the entire genre of such claims for persistent indicators in this literature.

Candidate macro drivers (M2 growth, the yield curve) exhibit the same era-dependent sign instability as the price indicators and are eliminated in a joint horse race; in the 2024–26 episode, liquidity kept expanding while Bitcoin topped on schedule and entered a bear market. The halving clock further outperforms every look-alike four-year cycle we test (the US election cycle, a fixed calendar, and 2,000 random four-year clocks), and the whole boom-bust-recovery path, not just the turns, repeats when cycles are aligned by days since halving. We summarize the asset's state in two time-anchored coordinates, days since halving and power-law deviation, under which Bitcoin's history traces a damped spiral: the amplitude is dying, the clock is not. The framework yields pre-registered, falsifiable predictions: a cycle bottom window of October 5 to November 16, 2026, and a next cycle top window 525 to 546 days after the following halving (provisionally late September to mid-October 2029, pending the halving's exact date).

**Keywords:** Bitcoin, halving, market cycles, power law, adaptive markets, technical indicators, market efficiency

---

## 1. Introduction

On January 8, 2009, five days after mining Bitcoin's genesis block, Satoshi Nakamoto announced the system's monetary schedule to the Cryptography Mailing List: total circulation would be 21 million coins, distributed to network nodes when they make blocks, "with the amount cut in half every 4 years." The schedule is not a policy that an institution maintains; it is a constant in the protocol, `SubsidyHalvingInterval = 210000` blocks, fixed at block zero and executable by no one's discretion. It is, to date, the only macroeconomic commitment in financial history that is known with certainty decades in advance.

This paper asks a simple question: *what is the stable coordinate system of Bitcoin's price dynamics, price or time?*

The question is motivated by an empirical puzzle. Over Bitcoin's first decade, a family of price-anchored and on-chain indicators earned reputations as infallible cycle-callers. The Pi Cycle Top indicator marked the December 2013 top to within one day, the December 2017 top to the day, and the April 2021 peak to within one day. MVRV above 3.7 and the Mayer Multiple above 2.4 flagged every major top from 2013 through early 2021 within a month; the Puell Multiple above 4.0 flagged every top through 2017. On the other side, MVRV below 1.0 and the Puell Multiple below 0.5 marked the 2015, 2018, and 2022 bottoms within four weeks. These records were earned out of sample, in real time, across multiple cycles. They were not curve-fit artifacts.

Then, at the October 2025 cycle top, the largest in Bitcoin's history by price, not a single one of them fired. An investor relying on the indicators that had "never missed" received no warning at all. Yet the top itself arrived almost exactly where Bitcoin's previous two mature cycles would have put it: 534 days after the April 2024 halving, against 525 days in 2017 and 546 days in 2021. Three cycles apart, the mature tops land within 21 days of one another when measured on the halving clock ({{FIGREF:figC}}).

[[FIG:figC]]

We argue that these two facts, the simultaneous silence of every price-anchored indicator and the punctuality of the turn in halving-time, are the same fact viewed from two sides. Together they identify Bitcoin's market cycle as a *damped oscillation on a fixed clock*. Each cycle, the oscillation's amplitude shrinks: we show that the per-cycle maximum of every major oscillator declines monotonically across all four epochs (MVRV cycle peaks of 5.88 → 4.72 → 3.96 → 2.74, for example), while per-cycle minima end the era higher than they began. Range compression mechanically silences any fixed threshold calibrated on earlier cycles. "It never missed before" described a shrinking range, not a reliable indicator. The period, by contrast, does not move: in time-since-halving coordinates, the turns cluster within ±2%.

Our contributions are fivefold:

1. **A causal power-law methodology.** We estimate Bitcoin's time trend (price ≈ A·tⁿ, t = days since genesis) by *expanding-window* regression, so that the trend at every date uses only information available on that date. This distinguishes our approach from the discredited Stock-to-Flow tradition, in which the trend is fit through the very future it is then claimed to predict. The causal exponent converges to n ≈ 5.6.
2. **A measurement of cross-cycle indicator decay.** Using rank information coefficients with autocorrelation-robust inference (Newey–West and circular block bootstrap), we show that short-horizon price indicators decay to statistical noise across epochs (RSI-14's 30-day IC falls from +0.28 to −0.02), that several invert sign, and that the long-horizon power-law deviation is the only signal in the formal inference battery whose relationship to forward returns holds direction in the two most recent cycles.
3. **The mechanism.** The compression of indicator extremes (top-side maxima declining monotonically across five oscillators in all four epochs; bottom-side minima ending the era higher than they began) explains *why* threshold indicators fail in sequence ordered by threshold aggressiveness, and predicts that recalibration cannot help: a threshold fit to past amplitude is a bet that damping has stopped.
4. **Elimination of macro confounders.** Money-supply growth and the yield curve exhibit the same era-dependent sign instability as the price indicators; in a joint HAC regression only cycle phase survives; turn-timing in liquidity coordinates is an order of magnitude looser than in halving coordinates; and the 2024–26 episode provides a natural experiment in which the liquidity thesis and the clock disagreed: liquidity expanded while Bitcoin topped on schedule.
5. **The Satoshi Clock.** We condense the framework into a two-coordinate state description, CLOCK (days since halving) and SPRING (power-law deviation), under which Bitcoin's full history traces a damped spiral, and we pre-register two falsifiable predictions (Section 8).

We are explicit about what we do not claim. With three mature cycles, we cannot establish that the halving *causes* the cycle, and we do not attempt to. Our claim is positional: among all candidate coordinate systems examined (price levels, price-derived oscillators, on-chain ratios, monetary aggregates, the yield curve), the protocol's time structure is the only one whose relationship to Bitcoin's dynamics is stable across eras, and the only one knowable in advance. Whether the clock works through real supply economics, through self-fulfilling coordination on a schedule that every participant can read (a Schelling point in code), or both, is a question we leave open. Under either mechanism, the clock is the load-bearing element.

The remainder of the paper proceeds as follows. Section 2 situates the work. Section 3 describes data. Section 4 develops the methodology, with emphasis on causality discipline. Section 5 presents results in eight parts. Section 6 interprets. Section 7 states limitations. Section 8 pre-registers predictions. Section 9 concludes.

---

## 2. Related Work

**Bitcoin price models in time.** Santostasi (2024) proposes that Bitcoin's price follows a power law in time since genesis, price ∝ t^5.8, motivated by feedback between adoption, security, and price; Burger (2019) independently described a closely related long-term power-law corridor of growth. Both are descriptive and fit on the full sample. PlanB's (2019) Stock-to-Flow model related price to programmed scarcity and gained wide attention before its post-2021 predictions failed by an order of magnitude; Cordeiro (2020) and others criticized its econometrics, in particular the in-sample fit and non-stationarity. Our methodological departure from both is the *causal* (expanding-window) estimation of the time trend: every parameter at date t is computed from data through date t only, so the trend cannot borrow information from the future it is evaluated against. The same discipline is applied to every signal in the study.

**Market efficiency and adaptation.** Urquhart (2016) found Bitcoin returns inefficient but trending toward efficiency; Nadarajah and Chu (2017) and Bariviera (2017) refined and extended the finding. Lo's (2004) Adaptive Markets Hypothesis predicts exactly the pattern we measure: profitable regularities decay as capital learns them, at a rate proportional to how easily they are arbitraged. Our contribution to this literature is a *differential* decay measurement. Price-anchored signals decay to noise while a time-anchored structure does not, which suggests that what is being arbitraged away is amplitude, not timing.

**Halving studies.** Event studies of the halvings (e.g., Meynkhard, 2019; subsequent work reviewed in MDPI's *JRFM*) find positive but delayed price responses, with predictive power that several authors describe as weakening. Practitioner literature, much of it built on the on-chain valuation tradition popularized by Woo (2017), widely asserts that the four-year cycle is dead or macro-driven. Our results cut against both views in a specific way: the cycle's *amplitude* response is indeed weakening, consistent with the maturation literature, but its *timing* regularity strengthened. The 2025 top was the most punctual yet.

**Liquidity narratives.** A large practitioner literature attributes Bitcoin's cycle to global money-supply growth, often citing a roughly 10-week lead of M2 over price. We provide, to our knowledge, the first per-epoch stability test of this relationship, and find it to be a one-era artifact (Section 5.6).

---

## 3. Data

**Bitcoin price.** Primary series: Bitstamp BTC/USD daily OHLC, August 18, 2011 to June 10, 2026 (5,411 days), spanning all four halving epochs and including intraday ranges for honest stop/target evaluation. Independent cross-check and long-history close: Coin Metrics community PriceUSD, July 18, 2010 to May 23, 2026 (5,789 days). The two sources agree to a median absolute difference of 0.15% over 5,393 overlapping days (95th percentile 1.82%; early-2010s single-exchange prints account for the tail).

**On-chain.** Coin Metrics community series: CapMVRVCur (MVRV ratio) and IssTotUSD (daily issuance value in USD, the Puell Multiple numerator), full span.

**Ethereum.** Coin Metrics PriceUSD, August 8, 2015 to May 23, 2026 (3,942 days), for the cross-asset replication; genesis date 2015-07-30.

**Macro.** FRED M2SL (US M2, monthly from 2018, quarterly from 2001) and T10Y2Y (10-year minus 2-year Treasury spread, quarterly from 2001), obtained via the TradingView FRED mirror and verified internally: 34 overlapping quarter-ends between the monthly and quarterly M2 series agree exactly. Publication lags are applied before any predictive use, +28 days for M2 and +7 days for the spread. One limitation: the series is US M2 rather than a global aggregate.

**Epochs and turns.** Epochs are delimited by the halvings: 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20 (E1–E4; inter-halving gaps 1,319 / 1,402 / 1,440 days). Cycle turns are defined mechanically, with no hand-picking. A **cycle top** is an all-time high followed by a drawdown of at least 45% before any new high (the final running peak qualifies "in progress" once the drawdown exceeds 35%); a **cycle bottom** is the minimum close between consecutive tops. Applied to the data from 2012 onward, this rule recovers exactly the turns of market folklore: tops April 2013, December 2013, December 2017, April 2021, November 2021, October 2025; bottoms July 2013, January 2015, December 2018, July 2021, November 2022 (on the full span the rule additionally flags four 2010–2011 microcap-era turns, all before the first halving, which enter no analysis). No discretionary dating is involved at any point.

---

## 4. Methodology

### 4.1 The causal power law

Let P_t be the daily close and τ_t the number of days since the genesis block (January 3, 2009). At each date t we estimate by ordinary least squares, using only observations up to t,

  ln P_s = ln A_t + n_t · ln τ_s + ε_s,  s ≤ t,

via running sums (exact, O(N)), requiring a minimum of 365 observations. The residual r_t = ln P_t − (ln A_t + n_t ln τ_t) measures how far price stands from *its own trend as estimable on that day*. We standardize r_t by its expanding mean and standard deviation to obtain the deviation score z_t ("SPRING" below). The fitted exponent stabilizes early and converges to n = 5.61 on Bitstamp data (5.67 on Coin Metrics), consistent with the value near 5.8 reported from full-sample fits ({{FIGREF:fig1}}). No parameter anywhere in this paper is estimated with future data. Each signal decides at a bar's close; any trade-structure evaluation enters at the next bar's open.

[[FIG:fig1]]

### 4.2 Signal battery

All signals are causal by construction: RSI-14 (Wilder); the Mayer Multiple (price / 200-day SMA) and its expanding z-score; the Pi Cycle ratio (111-day SMA / 2×350-day SMA); price relative to the 200-week and 2-year moving averages; MVRV; the Puell Multiple (issuance USD / its 365-day mean); the power-law deviation z; and *phase*, defined as days since the most recent halving: a pure time signal containing no price information whatsoever.

### 4.3 Predictive evaluation

For horizon h ∈ {30, 90, 180} days we compute the Spearman information coefficient (IC) between each signal and the forward h-day return, within each epoch. Because overlapping h-day returns are MA(h−1) autocorrelated, naive significance overstates by roughly √h. We therefore report (i) Newey–West (NW) t-statistics from rank-on-rank regression with Bartlett lag h, and (ii) circular moving-block bootstrap confidence intervals (block length min(h, n/5), B = 2,000), and accept a result only when both agree. For the head-to-head claim that one signal beats another, we additionally bootstrap the *paired* difference |IC_A| − |IC_B| within identical resamples.

**Multiplicity and calibration: what the grid cannot support.** HAC corrects autocorrelation, not the garden of forking paths, and at these sample sizes it does not even fully correct autocorrelation. Two diagnostics govern what the 3 signals × 3 horizons × 4 epochs = 36-cell grid can carry (the wider nine-indicator battery of Section 5.4 is descriptive only). *(i) False-discovery control:* under Benjamini–Hochberg across all 36 cells, no single cell survives at q = 0.05 or q = 0.10. The smallest individual p in the grid belongs to RSI in its 2016–2020 golden era (p = 0.015), a cell whose signal subsequently died. *(ii) An empirical replication null:* the apparent strength of the power-law cell is that it is the only one "significant" with consistent sign in both of the two most recent epochs. We test how often that configuration arises by chance with a dependence-preserving rotation null: within each epoch, the forward-return series is circularly rotated against the signal block by a random offset (one shared offset per epoch per replicate), preserving every series' autocorrelation, the cross-signal correlations, and the overlap structure, while destroying signal-to-future alignment; 2,000 replicates. The result is disqualifying for per-epoch inference. The NW statistic rejects at empirical rates of 0.33 (E3) and 0.17 (E4) per cell against a nominal 0.05, because persistent signals run against overlapping returns generate spurious "significance" constantly, and the probability that some cell double-hits with consistent sign is 0.21. The observed double-hit of the power-law cell is therefore statistically indistinguishable from persistence artifact. We accordingly use the IC tables in this paper *descriptively*, for sign stability and monotone cross-epoch trends, which are model-free statements about the realized sample, and rest economic claims on out-of-sample structure (Sections 5.4–5.5) and on the turn-timing test of Section 5.1, whose discrete-event null does not involve persistent-regressor correlation. We flag the calibration failure prominently because it applies with equal force to any published claim of per-epoch indicator significance on persistent crypto signals.

### 4.4 Economic evaluation

Two designs. (a) A discrete trade structure, identical across signals, that buys when a signal marks price "cheap" (z < −1, or RSI < 30), exits on reversion to trend (z ≥ 0 / RSI ≥ 55), with a 35% catastrophe stop evaluated intrabar against daily lows and fees included. (b) An all-days long/flat exposure (long when below trend or oversold, causal one-day lag), whose annualized Sharpe ratio is compared per epoch against always-long buy-and-hold. Buy-and-hold is the appropriate null for a 15-year secular bull.

### 4.5 The clock's null test, and what it can and cannot mean

The clock's regularity consists of six retrospectively identified turns: three mature-cycle tops at 525/546/534 days after their halvings (range 21 days) and three completed bottoms at 406/364/366 days after their tops (range 42 days). Three disclosures govern the interpretation of everything in this subsection.

*First, the turns are ex post.* They are dated by the mechanical rule of Section 3, applied to history; no one called them publicly in advance. The resulting probabilities therefore quantify how surprising the retrospective regularity is under a timing-free null. They are descriptive, and cannot substitute for a forecasting record. The pre-registered windows of Section 8 constitute the first real-time test of the clock.

*Second, the test postdates the observation.* Like any analysis of a noticed pattern, the null test was designed after the clustering was seen. We mitigate the resulting window-choice degrees of freedom by fixing the statistic (the observed range) and reporting a full sensitivity grid rather than a chosen window; we cannot eliminate post-hoc-ness itself.

*Third, the inclusion rule is asymmetric and we report the unfavorable variant.* Our headline excludes the first cycle's top (371 days; the documented warmup epoch) while including its bottom (406 days after the top). Because the warmup rationale concerns the power-law fit rather than top timing per se, we also report the variant with the E1 top included (four tops, range 175 days), the least favorable defensible specification.

The null: each top uniform on a window of width W_top days after its halving; each bottom uniform on W_bot days after its top. The two gap families are disjoint random variables under this null, so the joint probability is their product by construction. P(range ≤ r) for n uniform points is n(r/W)^(n−1) − (n−1)(r/W)^n, exact; Monte Carlo (2×10⁶ draws) agrees within sampling error.

**Table 0. The full variant grid (no cell hidden).**

| Variant | W generous | W conservative |
|---|---|---|
| Tops, mature only (n=3, r=21d) | 0.0006 (W=1458) | 0.0026 (W=700) |
| Tops, E1 included (n=4, r=175d) | 0.0063 (W=1458) | 0.0508 (W=700) |
| Bottoms (n=3, r=42d) | 0.0080 (W=800) | 0.0200 (W=500) |
| Joint, headline | 4.9×10⁻⁶ | 5.3×10⁻⁵ |
| Joint, hostile (E1 top incl.) | 5.0×10⁻⁵ | 1.0×10⁻³ |

The regularity survives the most hostile defensible specification at p ≈ 10⁻³ and the headline specification at 10⁻⁵ to 10⁻⁶. We treat these as motivation for the forward test, not as confirmation.

**The empirical drawdown-process null (the referee's null).** The uniform null is vulnerable to a serious objection: perhaps peaks followed by 45% drawdowns occur at a roughly four-year cadence naturally in an asset with Bitcoin's volatility structure, halving or no halving. We therefore construct a null that concedes everything except the calendar: circular block-bootstrap of Bitcoin's own daily log returns (block lengths 30/60/90/120/250 days, preserving volatility clustering and drawdown geometry), generating 2,000 synthetic price histories per block length over the same calendar, each processed by the *identical* mechanical turn rule.

The top statistic comes in two constructions. The primary construction is deterministic and contains zero analyst freedom: the cycle top of an epoch is its highest-priced qualifying top. Since every qualifying top is by definition an all-time high, this is mechanically the *last* qualifying top of the epoch. Under this rule November 2021, not April 2021, simply is the 2021 cycle top; no selection exists for anyone to make. The observed range is 21 days either way, because November 2021 is simultaneously the higher-priced and the range-minimizing top. A conservative secondary construction grants the null every selection freedom instead (the range-minimizing top per epoch; the best 3-subset of completed top-to-bottom gaps), bounding the result from above against any accusation that a selection favored us.

Results: synthetic paths produce on average about four qualifying mature-epoch tops, so large drawdowns at roughly this cadence are indeed natural. But under the deterministic construction, *no synthetic path in 10,000* (2,000 per block length, five block lengths) reproduces the observed ≤21-day halving-phase cluster; under the conservative construction, 0.10–0.25% do. The deterministic version is tighter for a clean reason: locked to each epoch's actual peak at a random phase, the null can no longer assemble a tight combination from multiple candidate tops. The same null exposes an honest casualty, but a casualty specific to the anchor. Measured forward from the top, the bottom-gap cluster (≤42 days) is reproduced by 31–43% of null paths: bear durations near twelve months are largely intrinsic to the drawdown process and carry little independent evidence about the clock. Measured backward from the *next* halving, however, the same three bottoms cluster in a 29-day window that this null reproduces in only 1.5% of paths, against 39% for the after-top anchor under identical machinery; the bottoms appear pinned to the upcoming halving more tightly than to anything behind them (as the halving gaps grew across cycles, the bottoms drifted later from the previous halving but held constant relative to the next). We do not promote this to a result. The next-halving anchor was one of several we examined after seeing the data, it rests on three bottoms, and a forward halving is itself a drifting target; we instead pre-register it as a falsifiable expectation for the 2026 bottom (Section 8). The case still rests on the tops, and the cadence is not the surprise; the phase-lock is. This construction was independently reconstructed from scratch by a second analyst on independently pulled data, with corroborating results under both constructions.

---

## 5. Results

### 5.1 The clock's regularity and its null test

**Table 1. Every completed cycle turn at mature scale (mechanical definition, ex post).**

| Turn | Date | Price | Days after halving | Days after its top |
|---|---|---|---|---|
| Top (E2) | 2017-12-16 | $19,641 | 525 | |
| Top (E3) | 2021-11-08 | $67,542 | 546 | |
| Top (E4) | 2025-10-06 | $124,824 | 534 | |
| Bottom (E1) | 2015-01-14 | $176 | 777 | 406 |
| Bottom (E2) | 2018-12-15 | $3,185 | 889 | 364 |
| Bottom (E3) | 2022-11-09 | $15,758 | 912 | 366 |

*Prices are the Coin Metrics reference daily close at each mechanically dated turn; it is the dating, not the price level, that supports the day-count claims. For reference, the October 2025 cycle's intraday all-time high was $126,296 on Coinbase and $126,272 on Bitstamp.*

Table 1 lists every completed turn at mature scale. The mature tops cluster at 535 ± 10 days (±2%); as a fraction of their varying halving gaps they sit at 0.374 / 0.379 / 0.366 (the last computed against the protocol-expected 1,458-day gap to the next halving). The bottoms cluster at 364–406 days after their tops, in three bear markets of very different character (a chaotic post-mania collapse, an orderly grind, and a leverage cascade). The first cycle's top (371 days) is the documented exception, consistent with every other warmup effect in the study (Section 5.4).

Under the null of Section 4.5, with the three disclosures stated there governing interpretation, the joint probability of both clusters ranges from 4.9×10⁻⁶ (headline specification, generous windows) to 1.0×10⁻³ (the hostile variant with the E1 top included, most conservative windows). Monte Carlo agrees with the exact formula within sampling error, and Table 0 reports every cell of the variant grid. The retrospective regularity is very unlikely under a timing-free null in every defensible specification; whether the clock holds *prospectively* is the subject of Section 8.

The harder empirical drawdown-process null of Section 4.5 makes the asymmetry between the two clusters visible directly ({{FIGREF:figA}}): not one of 10,000 block-bootstrapped Bitcoin histories reproduces the tops' 21-day cluster under the deterministic construction, while 38% reproduce the bottoms' 42-day cluster. This is the single clearest statement of where the clock evidence lives, and it is why we weight the forward predictions toward the tops.

[[FIG:figA]]

### 5.2 The cycle-callers: precise, then early, then silent

**Table 2. Canonical published thresholds versus the mechanically dated tops (offset of nearest firing; HIT if within 60 days).**

| Trigger | Apr 2013 | Dec 2013 | Dec 2017 | Apr 2021 | Nov 2021 | Oct 2025 |
|---|---|---|---|---|---|---|
| Pi Cycle cross | HIT −3d | HIT +1d | HIT +0d | HIT −1d | −210d | no fire |
| MVRV > 3.7 | HIT −21d | HIT −26d | HIT −10d | HIT −31d | −240d | no fire |
| Mayer > 2.4 | HIT +25d | HIT +19d | HIT −19d | HIT −31d | −240d | no fire |
| Puell > 4.0 | HIT −20d | HIT +22d | HIT −19d | no fire | no fire | no fire |
| Price > 5×2yr MA | HIT −31d | HIT −42d | HIT −44d | no fire | no fire | no fire |

The degradation is ordered by threshold aggressiveness ({{FIGREF:fig5}}). The most-stretched thresholds (Puell 4.0, 5× the 2-year MA) fell silent after 2017; the remainder fired at the April 2021 secondary peak and missed the bear-defining November top by seven to eight months; by October 2025 every top-caller was silent. Bottom-callers lasted longer: MVRV < 1.0, Mayer < 0.8 and Puell < 0.5 all marked the November 2022 bottom within a week. Their current-cycle test is live, however, and several thresholds are unreached at the trough so far (minimum MVRV 1.15; price has not touched the 200-week MA at all this cycle). The 200-week MA itself has already failed in both directions: the December 2018 bottom formed just above it (no touch at daily closes), and 2022 broke 34% below it.

We attribute these triggers to their originators, all practitioner constructions without peer-reviewed sources: the Pi Cycle Top to Swift (2019), the Mayer Multiple to Mayer (2016), the Puell Multiple to Puell (2019), and MVRV to Mahmudov and Puell (2018); the 200-week moving average is common trader convention. We use each threshold as its source defines it.

[[FIG:fig5]]

### 5.3 The mechanism: amplitude is dying

**Table 3. Per-epoch indicator extremes.**

| | Pi ratio | MVRV | Mayer | Puell | 2yr-MA mult |
|---|---|---|---|---|---|
| E1 max | 1.23 | 5.88 | 8.26 | 10.49 | 17.96 |
| E2 max | 1.06 | 4.72 | 3.78 | 6.62 | 9.96 |
| E3 max | 1.00 | 3.96 | 2.83 | 3.46 | 4.88 |
| E4 max | 0.74 | 2.74 | 1.52 | 1.59 | 2.31 |
| E1 min (MVRV/Puell) | | 0.56 | | 0.31 | |
| E4 min (MVRV/Puell) | | 1.15 | | 0.53 | |

Every top-side maximum in Table 3 declines monotonically across all four epochs. The bottom-side minima end the era far higher than they began (MVRV 0.56 → 1.15; Puell 0.31 → 0.53), though not monotonically ({{FIGREF:fig3}}). The oscillation range is narrower at the era's end from both sides. The consequence is mechanical: any fixed threshold calibrated on past cycles must eventually stop firing, in order of how deep into the old range it reaches. Table 2's death sequence is Table 3's compression, realized. "It never missed before" described a shrinking range, not a reliable signal. Recalibrating thresholds each cycle is simply a bet that the compression has stopped, fit to the past.

[[FIG:fig3]]

### 5.4 Continuous indicators decay and invert; the time-trend survives

Thresholds aside, the underlying signals' rank correlation with forward returns tells the same story. RSI-14's 30-day IC across epochs runs +0.28 → +0.14 → +0.17 → −0.02: decay to statistical zero, robust to every RSI period from 7 to 30. At the 180-day horizon several indicators *invert*: the Pi ratio's IC swings to +0.49 in E4, and the Mayer z and RSI flip sign relative to their 2017-era values. An indicator whose sign is era-dependent is unusable ex ante regardless of magnitude ({{FIGREF:fig4}}).

[[FIG:fig4]]

Against this, the power-law deviation z is the only signal in the formal inference battery (power-law z, Mayer z, RSI) whose 180-day IC has a stable sign and strong magnitude in all three mature epochs: −0.41, −0.40, −0.51 (Bitstamp; −0.45/−0.42/−0.60 on Coin Metrics). In the wider descriptive battery, the only other constructions that hold direction at this horizon are themselves slow and trend-anchored (price relative to the 200-week average; the Puell Multiple) or pure time (phase); every fast oscillator flips. Its nominal HAC statistics are large in both recent epochs (E3: t = −2.69; E4: t = −2.63), and it is the only cell in the grid with same-sign nominal significance in both. We do not advance this as calibrated inference, because the rotation null of Section 4.3 shows that configuration arises by persistence artifact with probability 0.21, and that the NW statistic's true size here is 0.17–0.33, not 0.05. What we do advance is model-free: across three mature epochs and two price sources the sign never flips and the magnitude never weakens, while every comparator flips, fades, or both; the identical pattern reproduces on a second asset with a different exponent (Section 5.5); and the economic crossover below is out of sample. The paired contrast |IC_pl| − |IC_rsi| rises monotonically across epochs (+0.15 → +0.23 → +0.28 → +0.31), a descriptive trend subject to the same inferential caution. With at most seven or eight non-overlapping 180-day windows per epoch (three or four in the current one), this is the honest power limit of the data, and we say so rather than dress it.

Design (a) of Section 4.4 produces too few events to evaluate: the power-law rule fired six times in fifteen years (positive in every epoch, with two stop-outs), so the economic evidence rests on design (b). Economically, no timing signal beats buy-and-hold in the early, bull-dominated epochs: sitting flat costs upside, and we report this plainly. But the power-law signal's Sharpe edge over buy-and-hold improves monotonically across epochs (−0.99 → −0.41 → −0.26 → +0.12) and crosses positive in the current cycle ({{FIGREF:fig6}}). Out of sample (2025–26), it beats buy-and-hold on Sharpe while cutting maximum drawdown by ten points (−41% versus −51%), and it is the only signal that does both (the Mayer z edges buy-and-hold on Sharpe alone). The weight this can bear is limited: the holdout is a single 526-day window dominated by one bear market, so the positive crossing is suggestive rather than decisive. What carries evidential weight is the shape rather than the endpoint, a four-epoch monotone improvement reproduced on an independent price source and on a second asset with a different exponent. What would make it decisive is not more backtesting but the pre-registered windows of Section 8.

A complementary, deliberately simpler economic test points the same way while exposing the limits of all of this. A purely halving-anchored cash rule (hold Bitcoin except during the historical top-to-bottom window, roughly 525 to 900 days after each halving, using only the known halving calendar and a one-day lag) beat buy-and-hold on total compounded return in all four cycles, cut every cycle's maximum drawdown, and compounded to roughly fifty times buy-and-hold's terminal wealth over the full history. This is not generic drawdown avoidance. Sliding the same-width cash window across the cycle, the edge is sharply localized to the true bust phase and loses everything when placed on the boom; a random cash mask of identical duration beats buy-and-hold only four percent of the time and never approaches the realized multiple; and the rule survives leave-one-cycle-out, a window optimized on any three cycles still beating buy-and-hold out of sample on the fourth (ratios 1.7 to 4.1). We nonetheless decline to advance it as a forward-validated edge, and the contrast with the Sharpe result above is the reason for care, not for excitement. The two are not in tension: total return rewards sidestepping catastrophic drawdowns, while risk-adjusted Sharpe penalizes the opportunity cost of sitting in cash during a secular bull, so the same timing can win on return and lose on Sharpe in the same cycle. The fifty-fold figure is overwhelmingly a compounding artifact of avoiding four single-asset crashes; the honest per-cycle out-of-sample edge is the two-to-fourfold range; and with four cycles, leave-one-out tests consistency across the turns already observed, not robustness to the next cycle's drift. We report it as a complementary illustration that the timing carries real economic weight, not as a trading system.

[[FIG:fig6]]

The crossover requires the moderate entry threshold (z < 0 or +0.25; the deepest threshold remains slightly negative), a threshold dependence we flag rather than bury. The result is insensitive to the fit and z-score warmup parameters in the two most recent epochs (nine variants within ±0.01 IC; the 2016–2020 epoch varies by up to 0.09 under the longest fit warmup) and strengthens monotonically with horizon (E4 IC −0.19 at 60 days, −0.69 at 360).

The first epoch is the exception throughout: the causal fit is still immature in 2012–13 (the exponent climbs from about 1.4 toward its asymptote), and the deviation score's E1 sign is flipped. We treat this as a feature of the methodology rather than an embarrassment. A causal fit needs roughly one cycle of data to learn the trend, after which deviations become informative. The identical warmup artifact appears in Ethereum's first epoch (below), supporting this interpretation.

### 5.5 Replication: independent source and second asset

On the independent Coin Metrics series, the IC results reproduce slightly stronger (180-day IC reaching −0.60 in E4), and the Sharpe-edge sequence reproduces the same monotone improvement with a weaker positive endpoint (−1.20 → −0.31 → −0.31 → +0.03). On Ethereum, with its own genesis (July 30, 2015) and a causally fit exponent near 2.1, very different from Bitcoin's 5.6, the same maturation crossover appears: 180-day IC strengthening from −0.37 (E3) to −0.65 (E4), and a Sharpe edge over buy-and-hold of −1.13 → −0.20 → +0.33 across the market-cycle epochs, while RSI never goes positive in any epoch. Ethereum's first epoch shows the same warmup sign-flip as Bitcoin's. That the crossover replicates on a second asset with a different exponent indicates a property of maturing crypto assets, not a Bitcoin-specific curve. The alignment runs deeper than the trend: Ethereum's mechanical cycle *tops* themselves land near the BTC halving phase, at 553, 546, and 489 days after the BTC halving (against Bitcoin's 525/546/534), with the 2021 tops falling on the same day. A coin with no halving of its own still turns near the BTC halving phase, which points to the halving as a market-wide clock rather than only a Bitcoin-supply effect.

### 5.6 The macro alternative: era-dependent and ex post

Two confounders dominate popular discussion: global liquidity (money supply) and the business cycle. We state the identification problem plainly: the liquidity cycle and the halving cycle are roughly co-periodic, and with three to four overlaps no co-periodic confounder can be fully excluded. Four discriminating tests are nonetheless available, and all four point the same way.

**(i) Sign stability.** M2 YoY growth's 180-day IC with forward Bitcoin returns runs +0.41 (E2), −0.10 (E3), −0.83 (E4). The yield-curve spread runs +0.42, −0.35, −0.79. Both flip sign across epochs exactly as the price oscillators do. The E4 sign is backwards for the liquidity narrative: from the April 2024 halving to the data freeze, M2 expanded continuously (YoY growth between +0.9% and +4.7%, with no contraction) while Bitcoin topped and fell.

**(ii) Lead/lag stability.** The folklore that "M2 leads Bitcoin by about 10 weeks" is a one-era artifact. The IC of lagged M2 growth against forward 90-day returns is positive at every lead from 0 to 270 days in E2 (peaking near +0.45 at a 120-day lead, presumably the folklore's origin), negative throughout E3, and negative at every lead in E4. No stable lead exists.

**(iii) Turn-timing precision.** Distances from the three Bitcoin tops to the nearest M2-YoY peak are +227, −253, and −67 days: mixed in sign and ranging from 67 to 253 days, versus the halving clock's ±10 days ({{FIGREF:fig7}}), an order of magnitude looser. There is also a practical asymmetry: monetary turning points are confirmable only months after the fact, while the halving schedule has been public since 2009. We credit the macro side its successes: the February 2021 M2-growth peak preceded the April 2021 secondary top by six weeks, and the 2022 curve inversion coincided with that bear market.

[[FIG:fig7]]

**(iv) Horse race.** Regressing forward 180-day returns on standardized phase, M2 growth, and the yield spread jointly (Newey–West, lag 180, mature sample, n = 3,426) gives phase t = −2.00, M2 t = +0.20, spread t = −0.07. Controlling for one another, only the clock retains any weight. The persistent-regressor calibration caveat of Section 4.3 applies to these t-statistics with full force, so we read the horse race as a relative statement (which regressor survives joint conditioning with stable direction) rather than as calibrated significance. Per-epoch partials are noisy under collinearity (|ρ| ≈ 0.5–0.66) and we do not over-read them.

**(v) A four-year-clock placebo.** The halving is one roughly-four-year clock; is the regularity halving-specific, or would any four-year cycle do as well? Measured under the halving, the three mature tops span 21 days. Under the US presidential-election cycle, also four-yearly, they span 68 days; under a fixed four-year calendar they span 1,423 days, because the tops follow the halving's actual, lengthening spacing rather than a fixed period; and of 2,000 random four-year clocks, *none* matches the halving's 21-day spread. The clustering is specific to the halving event, not to the calendar, which is the cleanest separation we can draw between the protocol clock and any generic four-year macro or political rhythm ({{FIGREF:figB}}).

[[FIG:figB]]

The conclusion is not that macro is irrelevant; within any single era its correlations are large. It is that macro's relationship to Bitcoin is era-dependent and ex post, sharing the instability of every price-anchored signal, while the time structure is era-stable and ex ante. In the one episode where the two clocks disagreed (late 2025, liquidity expanding, the calendar striking day 534), price followed the code.

### 5.7 The Satoshi Clock

The framework condenses to a two-coordinate state description we call the **Satoshi Clock**:

- **CLOCK**: days since the most recent halving, the angle of the four-year revolution;
- **SPRING**: the causal power-law deviation z, the radius, how stretched price is from its time trend.

**Table 4. The damped spiral (SPRING at each turn).**

| Turn | CLOCK (days) | SPRING (z) |
|---|---|---|
| Top 2013 | 371 | +2.85 |
| Bottom 2015 | 777 | −1.46 |
| Top 2017 | 525 | +2.69 |
| Bottom 2018 | 889 | −0.61 |
| Top 2021 | 546 | +1.29 |
| Bottom 2022 | 912 | −1.17 |
| Top 2025 | 534 | +0.43 |

Read down Table 4's SPRING column at the tops: +2.85 → +2.69 → +1.29 → +0.43. At the tops, the radius shrinks every revolution (the bottom-side readings are noisier: −1.46, −0.61, −1.17). This is Table 3's compression in trend-deviation units, and it is why every amplitude-calibrated indicator has died or will die. Read down the CLOCK column at the mature tops: 525, 546, 534. The angle does not move. *The amplitude is dying; the clock is not.* Bitcoin's full price history, plotted in these coordinates, is a damped spiral converging toward its power-law trend ({{FIGREF:fig2}}). The spiral is also a quantitative statement of the asset's maturation: each cycle, Bitcoin overshoots its own adoption trend by less.

[[FIG:fig2]]

As of the Coin Metrics data freeze (May 23, 2026; price $76,620): CLOCK 763, SPRING −0.53, 229 days after the October 2025 top. Mid-bear, by the geometry of every prior cycle.

### 5.8 The clock governs the whole cycle, not just the turns

The turn-dating tests treat each cycle as two points. Two further tests show the clock organizes the entire trajectory. First, when the three completed cycles are aligned by days since halving and normalized to the halving-day price, their paths correlate at 0.72 on average: the boom, the top, the bust, and the recovery all line up ({{FIGREF:fig8}}, left). Aligned at a random offset instead, the correlation collapses to 0.02, and only 2.8% of random alignments match the halving alignment, so it is the halving phase specifically that the cycles share, not merely a smooth-curve artifact. Second, pooling every (phase, forward-90-day-return) pair across cycles, average forward returns are strongly positive from the halving to about day 520, turn negative from roughly day 520 to 900, and turn positive again afterward ({{FIGREF:fig8}}, right). The sign flips almost exactly at the mechanically dated top window (525–546 days) and again near the bottom. Turn-dating and average returns, two independent methods, locate the same turn days.

Not everything locks to the clock, and we report the miss because it disciplines the hits. Realized volatility does *not* peak at a consistent halving-day: the peak phases are 157, 585, and 394 days, and the volatility-versus-phase shape correlates at only 0.15 across cycles, indistinguishable from the random-offset placebo (p = 0.19). The clock governs the cycle's direction and shape, not its volatility. A framework that found a clock in everything would be the more suspicious one; this one finds the clock where there is real structure and reports plainly where there is not. The placebo probabilities in this section (the 2.8% above and the volatility p = 0.19) come from random-offset permutation nulls of the same discrete-event family exempted in Section 4.3, not the autocorrelation-robust per-signal p-values that our rotation null disqualifies; they ask only how often a random phase alignment matches the halving's, which block reshuffling answers without the persistence bias that voids HAC inference here.

[[FIG:fig8]]

---

## 6. Discussion

**Why price indicators must fail.** Under the damped-oscillation reading, the failure of the cycle-caller family is not a coincidence of 2025 but a structural inevitability with a predictable order. A threshold indicator is a horizontal line drawn through an oscillation; if the oscillation's envelope contracts monotonically, the line is exited permanently, deepest lines first. That is precisely the observed death sequence (Puell 4.0 and 5×2yr-MA after 2017; Pi Cycle, MVRV 3.7 and Mayer 2.4 after April 2021; everything by 2025). Continuous versions of the same signals escape the threshold problem but not the deeper one: their *meaning* is era-dependent, decaying and inverting as the market matures. The Adaptive Markets view organizes this naturally. What capital arbitrages away is the exploitable amplitude; the calendar, being no one's inefficiency, is not arbitraged but if anything reinforced.

**Why the clock might work.** We deliberately bracket the causal channel, because the two leading candidates are observationally similar at n = 3 and both leave our claim intact. (a) *Supply economics:* the halving instantaneously halves the flow of new supply; with demand continuity, the price response propagates with lags set by miner inventory behavior and reflexive momentum, a mechanical clock. (b) *Coordination:* the schedule is the most public focal point in the asset's culture; if enough participants expect cycle behavior in halving-time, front-running and herding can synchronize the turn, a Schelling clock (Schelling, 1960). Explanation (b) is not deflationary: a self-fulfilling cycle anchored to a constant in the source code is still a cycle anchored to the source code, and its timing is still knowable decades ahead. Distinguishing (a) from (b), for instance via miner flow data or cross-asset placebo clocks, is the natural next study.

**The maturation synthesis.** The two halves of the paper are one phenomenon. Diminishing amplitude (returns, volatility, indicator extremes, SPRING at tops) is the asset converging toward its adoption trend; fixed period is the trend's clock. On this view the often-asked question "is the four-year cycle dead?" conflates the two. The cycle's *profitability* is dying on schedule with maturation, while its *timing* has never been more precise. We would expect future cycles to continue this pattern, shallower oscillations and punctual turns, until amplitude is no longer distinguishable from noise.

---

## 7. Limitations

1. **Retrospective identification and post-hoc testing.** The six turns were identified ex post by a mechanical rule, not called in real time; the null test was designed after the pattern was observed; and the headline specification excludes the first cycle's top while including its bottom. We disclose all three (Section 4.5), report the hostile variant (joint p up to 10⁻³), and emphasize that the retrospective probabilities motivate the prospective tests of Section 8 but cannot substitute for them. One verified real-time antecedent exists (Section 8.1: a public, platform-timestamped month-precision call of the 2025 top, made January 2025). It is n = 1, it is the author's own, and it applied the community's folk heuristic rather than this paper's model: an out-of-sample application of a known rule, not independent validation. We weight it accordingly.
2. **Few cycles.** The headline regularity rests on three mature tops and three completed bottoms. The variant grid (Section 5.1) shows this regularity is very unlikely under a timing-free null, but n = 3 pairs cannot establish causation, fine structure, or stationarity of the period. Every competing cycle theory faces the same constraint on the same data. We also probe the clock from several angles (top phase, bottom phase, the cycle's shape, its return profile, its volatility, and a battery of look-alike clocks); most survive their own placebo and one, volatility, does not, but at three to four cycles the battery as a whole carries a multiple-comparisons burden we cannot fully discharge. The placebos and nulls bound how surprised we should be on each test; the pre-registered predictions of Section 8 are what ultimately settle it.
3. **Per-epoch significance is unattainable here, for anyone.** No individual cell of the 36-cell grid survives false-discovery control, and our rotation null shows the HAC machinery's true size on persistent signals at these sample sizes is 0.17–0.33 against a nominal 0.05. The apparent two-epoch significance of the power-law cell arises by persistence artifact with probability 0.21. The power-law claims in this paper are therefore descriptive (sign stability, monotone trends) and economic (out-of-sample crossover), supported by cross-source and cross-asset replication, never inferential at the per-epoch level. The same caution applies to the macro horse race of Section 5.6, whose regressors are equally persistent; we read it as a direction-stability comparison, not calibrated inference.
4. **Co-periodic confounders.** Liquidity and halving cycles overlap too few times to be fully separable; our four tests discriminate on stability, precision, and the 2024–26 disagreement episode, not on exclusion.
5. **The first epoch.** The causal fit needs about one cycle of warmup; E1 results are sign-flipped and excluded from mature-epoch claims by stated rule, not post hoc.
6. **Intra-cycle structure.** The 2020–24 epoch contained a double top (April/November 2021) and an unusually early bottom relative to halving-time; phase's within-cycle IC was weak in that epoch (−0.07). The clock claim concerns the bear-defining turns, not every intermediate swing.
7. **Threshold dependence and a thin holdout.** The exposure-level Sharpe crossover requires the moderate entry threshold (the deepest variant remains slightly negative in E4), and the out-of-sample window is a single 526-day span dominated by one bear market: suggestive, not decisive. The claim's weight rests on the four-epoch monotone trend and its cross-source and cross-asset reproduction, pending the prospective test.
8. **Marginal head-to-head contrast.** The paired |IC| advantage of the power-law signal over RSI in E4 is significant only at the 10% level (p = 0.07).
9. **Macro data.** US rather than global M2; quarterly macro granularity before 2018; and ex-post dating of monetary turns, which biases toward the macro alternative.
10. **Bottom-callers not yet failed.** The on-chain bottom indicators nailed 2015, 2018, and 2022, and their E4 test is in progress. If the current bear bottoms below MVRV 1.0 and at the 200-week MA, the bottom-side compression claim weakens (the top-side claim is unaffected).

---

## 8. Pre-Registered Predictions and a Real-Time Antecedent

### 8.1 A real-time antecedent

Two public, platform-timestamped artifacts show the timing heuristic in use nine months before the cycle top, predating all of this paper's analysis. On January 6, 2025, with Bitcoin at $102,180, the author published a 57-second video to Instagram (account *bitcoin.daily*; upload timestamp verified from platform metadata), stating: *"Every crypto bull run has a peak. We saw it in 2013, right before an 86% crash. We saw it in 2017, right before an 81% crash, and once again in 2021, before a 77% crash... Bitcoin follows a predictable four-year cycle based on its halving. Based on the latest halving back in April of 2024, data tells us that Bitcoin is most likely a peak in late 2025... set an alert on your phone for October of 2025."* The video includes an on-screen calendar graphic showing an all-day event for Monday, October 20, 2025, titled "SELL BITCOIN (18 Months POST HALVING)." Five days later (January 11, 2025, Bitcoin at $94,607), a longer YouTube video on the channel "Bitcoin Daily" restated the call: *"every single bull market, Bitcoin peaks 18 months after its halving... that puts the next peak in October of this year,"* and *"the cycle isn't up for debate. It's literally written into its code."* Quotations are from automated transcription of the audio; punctuation is editorial, obvious captioning errors are corrected (the auto-captioner renders "halving" as "Halen"), and the spoken wording is otherwise preserved.

**Provenance, stated precisely.** The January 2025 dating of these artifacts rests on the platforms' own upload metadata, which is credible but platform-controlled; no independent timestamp of the upload dates exists. It is corroborated by engagement that accrued on the posts before the event: the YouTube video carries viewer comments that the platform dates to roughly mid-2025, months before the top, including one asking why the strategy calls for selling "around October/November," that is, third-party discussion of the timing call while the outcome was still unknown. These comment dates are platform-rendered relative dates and are approximate. No pre-event web-archive capture of either URL exists; we checked the Wayback Machine's index directly. The preservation measures taken in June 2026 (Internet Archive and archive.today snapshots, plus an OpenTimestamps anchor of the evidence bundle's SHA-256 manifest in the Bitcoin blockchain) establish only that the artifacts existed in their present form as of June 11, 2026. They protect the record against future alteration, carry no weight whatsoever on the January dating, and we claim none from them.

The realized cycle top, dated mechanically in this paper from data ending June 2026, was October 6, 2025: month-exact to both calls, fourteen days before the on-screen alert date. One further detail belongs here, since a careful reader would find it anyway. The January videos themselves recite the diminishing-crash sequence (86%, 81%, 77%), the very amplitude-compression series this paper formalizes, and then extrapolate it forward as an "80 to 90%" crash prediction, repeating at the amplitude level precisely the calibrated-on-the-past error this paper documents in every threshold indicator. The timing half of those videos has been vindicated; the amplitude half is, so far, missing high. The forecaster enacted the paper's thesis in both directions at once.

Full-record disclosure, because a forecast only counts in the context of all forecasts made: (i) the same video predicted a post-peak drawdown of "80 to 90%," an amplitude claim that is currently overshooting (maximum drawdown near 50% to date), consistent with this paper's compression finding and a miss in its own right if the bear ends near current levels; (ii) in other public content during the same cycle the author issued price targets of $150,000 to $200,000 for the top, which missed (the cycle's intraday all-time high was $126,296); (iii) the author also published a series of 2026 bear-market leg forecasts based on cross-cycle pattern correlation, which do not derive from the clock and are claimed as no evidence here. The author operates a media channel advocating this framework, a conflict we disclose.

We weight this antecedent honestly, beginning with what it is not. The 18-months-after-the-halving rule is common knowledge in the practitioner community, not this paper's invention. What this paper contributes is the rigorous version: the measured 525/546/534-day cluster, the nulls it survives, and the compression mechanism that explains why timing outlives every other signal. The January videos are therefore an out-of-sample application of a known heuristic, publicly committed to before the fact and correct on timing. They are evidence that the regularity was real and exploitable ex ante, not independent proof of the model developed here, which did not yet exist. Within those bounds it is n = 1, it is the author's own call, and naming one month roughly nine months ahead carries non-trivial luck probability. We include it for two reasons. First, it establishes that the timing regularity was being acted on publicly, in real time, before any of this paper's analysis existed; the retrospective results of Section 5.1 did not manufacture it. Second, the bifurcation within the author's own record (the timing call hit to the month while every amplitude call missed high) is the paper's thesis enacted in miniature, by a forecaster who did not yet have the formal result. The clock is predictable; the amplitude is not.

### 8.2 Pre-registered windows

A theory of timing should stake dates, especially one whose historical evidence is otherwise retrospective. The windows below are stated before the outcome exists, and they are the standard by which the thesis should ultimately be judged. From the clock's geometry, fixed before the fact:

1. **Current-cycle bottom window: October 5 to November 16, 2026** (364–406 days after the October 6, 2025 top). A second anchor sharpens it: measured backward from the next halving, the interval at which past bottoms cluster most tightly (Section 4.5), the window is October 21 to November 19, 2026 (provisional, since the next halving's date drifts), so the two anchors overlap on roughly October 21 to November 16, the robust core of the call. We also register a *structural* sub-prediction that falls out of Section 4.5: the 2026 bottom should sit tighter to the next-halving anchor than to the after-top anchor. That is the forward test of an anchor we could only select in-sample, and it is the honest way to earn back what the after-top measurement gave away. We still treat the bottom as the weaker of our two predictions, since bear-duration clustering from the top is substantially process-intrinsic; a hit is modest evidence, a miss modest counter-evidence.
2. **Next cycle top window: 525 to 546 days after the next halving.** We state this relative to the halving rather than as a fixed calendar date on purpose. The halving's exact day is not yet set: it depends on realized block times and has historically arrived somewhat before the naive ten-minute estimate, so a calendar window pinned now would inherit an error we do not control and cannot honestly pre-register. At the current halving estimate of roughly April 2028 the window maps to approximately late September to mid-October 2029, a provisional range we will refine once the halving block is in sight. The falsifiable claim is the halving-relative one. This is the sharp test: top-phase alignment is what the deterministic null never reproduced in 10,000 paths (and the conservative variant reproduced in fewer than 0.25% of them), and it is where the thesis lives or dies.
3. **Falsification:** either pre-registered turn missing its window by more than about 90 days, that is the 2026 bottom falling outside roughly July to December 2026 (a daily-close cycle low more than 90 days from the October 21 to November 16 core) or the next top landing more than 90 days off 525–546 days after its halving, or a SPRING amplitude at the next top *exceeding* the 2025 value (+0.43), would each contradict the damped-clock model as stated.

We commit to evaluating these in a follow-up regardless of outcome.

---

## 9. Conclusion

Every price-anchored description of Bitcoin's market cycle is dying, in a measured, monotone, mechanistically explicable way: the oscillation's amplitude compresses every cycle, so thresholds go silent in order of aggressiveness and continuous indicators decay toward noise or invert. The macro alternatives behave no better, flipping sign era to era and failing a joint test against the calendar. What remains is the one structure that was never estimated from price at all, because it was never estimated from anything: a constant written into the protocol at block zero and announced by its author in January 2009 as "the amount cut in half every 4 years." In the coordinates of that clock, the asset's history is a damped spiral, with turns at 525–546 days after each halving and 364–406 days after each top, a retrospective regularity whose chance probability ranges from 5×10⁻⁶ to 1×10⁻³ across every timing-free null and construction we tested against it, including a 2025 top that arrived on schedule while every famous indicator was silent and global liquidity argued the other way. The amplitude is dying; the clock is not. Bitcoin, at the end of the day, is code. On the evidence assembled here, it keeps its own time.

---

## References

- Bariviera, A. F. (2017). The inefficiency of Bitcoin revisited: A dynamic approach. *Economics Letters*, 161, 1–4.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
- Burger, H. C. (2019). Bitcoin's natural long-term power-law corridor of growth. *Medium* (online; practitioner, no peer-reviewed version).
- Cordeiro, N. (2020). A chameleon model: Why Bitcoin's stock-to-flow model is fatally flawed. *Strix Leviathan* (online).
- Lo, A. W. (2004). The Adaptive Markets Hypothesis: Market efficiency from an evolutionary perspective. *Journal of Portfolio Management*, 30(5), 15–29.
- Mahmudov, M., & Puell, D. (2018). Introducing MVRV: The Market-Value-to-Realized-Value ratio. *Medium / Adaptive Capital* (online; practitioner).
- Mayer, T. (2016). The Mayer Multiple. *mayermultiple.com* (online; practitioner).
- Meynkhard, A. (2019). Fair market value of Bitcoin: Halving effect. *Investment Management and Financial Innovations*, 16(4), 72–85.
- Nadarajah, S., & Chu, J. (2017). On the inefficiency of Bitcoin. *Economics Letters*, 150, 6–9.
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Nakamoto, S. (2009, January 8). Bitcoin v0.1 released. *The Cryptography Mailing List*, metzdowd.com. ("Total circulation will be 21,000,000 coins... the amount cut in half every 4 years.")
- PlanB (2019, March 22). Modeling Bitcoin value with scarcity. *Medium* (online).
- Puell, D. (2019). The Puell Multiple. *Medium* (online; practitioner).
- Santostasi, G. (2024). The Bitcoin power law theory. *Medium*, giovannisantostasi.medium.com (online; no peer-reviewed version exists; first proposed on Reddit in 2018).
- Schelling, T. C. (1960). *The Strategy of Conflict*. Harvard University Press.
- Swift, P. (2019). Pi Cycle Top indicator. *LookIntoBitcoin* (online; practitioner).
- Urquhart, A. (2016). The inefficiency of Bitcoin. *Economics Letters*, 148, 80–82.
- Wilder, J. W. (1978). *New Concepts in Technical Trading Systems*. Trend Research.
- Woo, W. (2017). Is Bitcoin in a bubble? Check the NVT ratio. *Forbes / Woobull* (online; practitioner).

---

## Appendix A: Data and Code Availability

All data are from public sources (Bitstamp public API; Coin Metrics community data; the FRED series M2SL and T10Y2Y, obtained via the TradingView mirror of the FRED catalogue with values embedded and internally cross-checked in `build_macro_csv.py`). The full analysis pipeline is available as documented Python scripts: `pull_btc_daily.py`, `pull_btc_ohlc.py`, `pull_btc_metrics.py`, `pull_eth_daily.py`, `build_macro_csv.py` (data); `pl_lib.py` (causal power law and signal library); `study_signals.py` (IC framework); `ic_significance.py` (HAC and bootstrap inference); `pl_backtest.py`, `exposure_study.py` (economic evaluation); `replicate.py` (cross-source and Ethereum replication); `sweep_sensitivity.py` (robustness grids); `cycle_callers.py` (threshold indicators, extremes, turn dating); `macro_study.py` (confounders); `satoshi_clock.py` (permutation test and the indicator); `verify_hardening.py` (permutation variant grid and BH-FDR across the full inference grid); `joint_replication_test.py` (the dependence-preserving rotation null and NW calibration diagnostic); `empirical_null_test.py` (the block-bootstrap drawdown-process null for turn timing, both constructions); `clock_explorations.py`, `clock_explorations2.py` (the four-year-clock placebo, cross-asset turn alignment, cycle-shape overlay, return-by-phase, and volatility-clock null of Sections 5.5–5.8); `clock_anchors_test.py`, `clock_bottom_anchor_null.py` (the three-anchor bottom analysis of Section 4.5). Every numerical claim in this paper maps to a line of script output; the `audit/` directory contains the captured output of an end-to-end re-run of the entire pipeline, and `RESULTS_LOCK.md` indexes each claim to its script and output file. A public repository link will accompany submission.
