# RESULTS_LOCK, every load-bearing manuscript number → script → captured output

## ✅ INDEPENDENT VERIFICATION: COMPLETE (2026-06-11)
A second analyst reproduced the paper's full core end-to-end on independently pulled data
(Bitstamp + Coin Metrics, frozen to the lock dates), several rows bit-exact: signal library &
exponent; IC decay; rotation null (0.2145), NW miscalibration (.333/.168), 0/36 FDR; turn dates
& extremes compression; permutation grid incl. hostile variant; drawdown-process null (twice,
from-scratch reconstructions, both constructions); OOS crossover & drawdown; ETH & Coin Metrics
replication; macro elimination; SPRING values & both prediction windows. The epoch-max
(deterministic) construction was proposed by the verifier and corroborated bilaterally
(their 0/6,000; our 0/10,000). **No unverified inference remains in the paper's core.**

Audit protocol: `audit/` contains the captured stdout of a full end-to-end re-run of the
pipeline (2026-06-10, all 12 scripts exit 0). All stochastic procedures are seeded, so a
re-run reproduces these numbers exactly. To re-verify: run each script and diff against
`audit/<script>.out`.

| Manuscript claim | Value | Script | Output |
|---|---|---|---|
| Turn dates + days-after-halving/top (Table 1) | 525/546/534; 406/364/366 | satoshi_clock.py, cycle_callers.py | audit/satoshi_clock.out, audit/cycle_callers.out |
| Permutation variant grid (Table 0) | joint 4.9e-6 → 1.0e-3 (hostile) | verify_hardening.py | audit/verify_hardening.out |
| BH-FDR across 36-cell grid | 0/36 at q=.05 and q=.10 | verify_hardening.py | audit/verify_hardening.out |
| **Empirical joint-replication p (rotation null)** | **0.2145 (se .009, B=2000)** | joint_replication_test.py | audit/joint_replication_test.out |
| **Empirical drawdown-process null (turn timing)** | **PRIMARY (epoch-max, deterministic): 0/10,000 paths across L=30/60/90/120/250; conservative (selection-symmetric): 0.0010–0.0025; bottoms 0.31–0.44** | empirical_null_test.py | audit/empirical_null_test.out |
| **NW empirical size under null** | **E3 0.333 / E4 0.168 vs nominal .05** | joint_replication_test.py | audit/joint_replication_test.out |
| Cycle-caller hit/miss (Table 2) | hits thru Apr-21; no fire Oct-25 | cycle_callers.py | audit/cycle_callers.out |
| Extremes compression (Table 3) | MVRV 5.88→2.74 etc. | cycle_callers.py | audit/cycle_callers.out |
| Causal exponent | 5.61 (Bitstamp) / 5.67 (CM) | study_signals.py, replicate.py | audit/study_signals.out, audit/replicate.out |
| IC tables (descriptive) | RSI 30d +0.28→−0.02; pl_z 180d −0.41/−0.40/−0.51 | study_signals.py | audit/study_signals.out |
| Nominal HAC cells (descriptive only) | pl_z@180 E3 t−2.69/E4 t−2.63; RSI@90 E2 p=.015 | ic_significance.py | audit/ic_significance.out |
| Sharpe crossover | −0.99→−0.41→−0.26→+0.12; OOS +0.11, DD −41 vs −51 | exposure_study.py | audit/exposure_study.out |
| ETH + CM replication | ETH edge −1.13→−0.20→+0.33; exponent ~2.1 | replicate.py | audit/replicate.out |
| Parameter sweeps | 9 fit variants ±0.01; RSI periods 7–30 | sweep_sensitivity.py | audit/sweep_sensitivity.out |
| Macro: IC flips, lead/lag instability, turn distances, horse race | m2 +0.41→−0.83; +227/−253/−67d; phase t−2.00 | macro_study.py | audit/macro_study.out |
| SPRING at turns (Table 4) + prediction windows | +2.85/+2.69/+1.29/+0.43; 2026-10-05..11-16; 2029 top = 525-546d after the next halving (calendar provisional) | satoshi_clock.py | audit/satoshi_clock.out |
| **Clock-timing complement (§5.4)** | timing beats buy-and-hold 4/4 cycles on return AND drawdown; stacked **53.1x** (302,618x vs 5,698x); time-in ~67-74% | clock_timing_backtest.py | audit/clock_timing_backtest.out |
| **Clock-timing adversarial red-team** | window-sweep: edge localized to bust phase, **boom-cash = 0.0x/0-of-4**; placebo random 26%-cash P(>=1)=4%, P(>=53x)=0%; **leave-one-cycle-out 4/4 OOS wins (1.7-4.1x)** | clock_timing_adversarial.py | audit/clock_timing_adversarial.out |
| E4 cycle ATH (intraday) | **$126,296 Coinbase / $126,272 Bitstamp** (Oct 2025); turn-dating uses CM daily close $124,824 | (Coinbase/Bitstamp API) | Table 1 note |
| **Bottom anchor null (§4.5)** | after-top ≤42d reproduced **39.4%** (matches locked 31-43%); **until-next-halving ≤29d reproduced only 1.5%** (selection-symmetric, L=30/60/90/120/250, B=2000) | clock_bottom_anchor_null.py | audit/clock_bottom_anchor_null.out |
| Three-clock anchor ranges | tops: after-halving 21d / until-next 45d / after-prev-bottom 8d. bottoms: after-halving 135d / **until-next 29d** / after-top 42d. 2026 bottom anchors overlap ~Oct 21-Nov 16 | clock_anchors_test.py | audit/clock_anchors_test.out |
| **Seasonality overlay (§5.8)** | cycles aligned by days-since-halving correlate **0.72** (random-offset placebo 0.02, P=2.8%) | clock_explorations.py | audit/clock_explorations.out |
| **4-year-clock placebo (§5.6 v)** | tops' range: halving **21d** / election 68d / fixed-4yr 1423d; **0/2000 random 4yr clocks** beat 21d | clock_explorations.py | audit/clock_explorations.out |
| **Cross-asset ETH turns (§5.5)** | ETH mature tops 553/546/489d after BTC halving (vs BTC 525/546/534); 2021 same day | clock_explorations.py | audit/clock_explorations.out |
| **Return-by-phase (§5.8)** | fwd-90d return: +ve days 0-520, **−ve 520-910** (flip at top window), +ve recovery 910+ | clock_explorations2.py | audit/clock_explorations2.out |
| **Volatility clock (§5.8 NULL/miss)** | peak-vol day 157/585/394 (range 428d), curve corr 0.15, placebo P=19%, does NOT lock (honest negative) | clock_explorations2.py | audit/clock_explorations2.out |
| **Evidence figures (Fig 1/3/9)** | reproduce locked numbers w/ identical seeds: null tops 0/10,000 + selection 16/10,000(0.16%) + bottoms 3824/10,000(38%); placebo halving 21d/election 68d/random 71d/fixed 1423d, 0/2000 | paper/make_evidence_figs.py (reuses empirical_null_test.py SEED=31, clock placebo rng=7) | stdout check in commit |

## Claims DOWNGRADED by the hardening passes (history, so it can't silently regress)
0. **Bottom-timing cluster demoted.** The empirical drawdown null reproduces the ≤42d bottom-gap
   cluster in 31–43% of paths. Bear-duration clustering is largely process-intrinsic. The clock
   evidence is concentrated in TOP phase-alignment (deterministic 0/10,000; selection-symmetric
   0.0010–0.0025). Manuscript §4.5/§8 updated:
   2026 bottom window = weaker prediction; 2029 top window = the sharp test.
   Also disclosed: the observed 21d top range uses a selection (Nov over Apr 2021); null paths
   get the same freedom (selection-symmetric scoring).
1. ~~"joint replication global-null p ≈ 0.006 (9×0.025²)"~~: analytic envelope, falsified by
   the empirical rotation null (p = 0.21; NW size 0.17–0.33). All per-epoch IC significance
   language removed from the manuscript; IC tables are now descriptive only.
2. ~~"5×10⁻⁶ to 5×10⁻⁵"~~: widened to 5×10⁻⁶..1×10⁻³ including the hostile E1-top-included
   variant; relabeled retrospective regularity, not a track record.
3. ~~"sole HAC-significant survivor"~~. Rescoped: no cell survives FDR; claim now rests on
   sign-stability + monotone trends + OOS crossover + cross-source/cross-asset replication.

## ⚖️ PROVENANCE AUDIT (2026-06-12, post-review): what each piece of evidence supports
- **Pre-event dating** rests on: (1) platform upload metadata (YT 2025-01-11 ts 1736615802;
  IG 2025-01-06 ts 1736178846), credible, platform-controlled; (2) CORROBORATION: 16 YouTube
  comments platform-dated ~mid-2025 (pre-top), incl. one asking why to "sell around
  October/Novem[ber]" = third-party discussion of the call before the outcome (yt_comments.
  info.json; dates are platform-rendered relative dates, approximate).
- **NO pre-event web archive exists**: Wayback CDX checked for watch-URL, youtu.be, and IG reel:
  only capture is the author's 2026-06-11 snapshot.
- **June 2026 archives + OpenTimestamps anchor prove existence as of 2026-06-11 ONLY**. They
  protect against future alteration and carry ZERO weight on the January dating. §8.1 now has a
  "Provenance, stated precisely" paragraph claiming exactly this and no more.
- Corrections from review: RSI E4 30d IC = **−0.02** (was misstated +0.02; matches audit &
  reviewer's −0.03 at their freeze); IG quote now VERBATIM "most likely a peak in late 2025"
  (base.en + small.en whisper agree; spoken-language note added); 0/10,000 incl. L=120/250
  confirmed in audit/empirical_null_test.out.

## Real-time antecedent (verified 2026-06-10)
- YouTube video "I'll Be Leaving Crypto in 2025 (and You Should Too)", channel **Bitcoin Daily**,
  id `m8wvCwnI_Qk`, **upload_date 2025-01-11** (platform timestamp 1736615802), 745s.
  Verbatim (auto-caption transcript saved → `video_call_transcript.txt`): "every single bull
  market Bitcoin peaks 18 months after its halving. That puts the next peak in October of this
  year"; "the cycle isn't up for debate. It's literally written into its code"; also predicted
  "80 to 90%" post-peak crash (amplitude call, currently overshooting). Realized top 2025-10-06 =
  month-exact, 14d before the 18-month mark (Oct 20).
- Instagram reel `DEfV6l9CjFn`, account **bitcoin.daily** (Josh Molnar), **upload_date 2025-01-06**
  (timestamp 1736178846), 56.6s. Audio transcribed via faster-whisper (→ `ig_reel_transcript.txt`):
  recites 86/81/77% diminishing-crash sequence; "predictable four-year cycle based on its halving";
  "most likely a peak in late 2025"; "set an alert on your phone for October of 2025". ON-SCREEN
  calendar graphic at ~35s: **"Monday, Oct 20, 2025: SELL BITCOIN (18 Months POST HALVING)"**
  (frame saved → `evidence_ig_calendar_oct20.png`). Realized top Oct 6 = 14d before alert date.
  Explicit "Oct 6–Nov 11" window NOT found in either artifact (audio or legible frames). Not
  claimed in the paper. BTC prices on upload dates verified from btc_daily.csv: 01-06 $102,180,
  01-11 $94,607.
- ✅ **YouTube archived** (author, via browser, 2026-06-11):
  https://web.archive.org/web/20260611181109/https://www.youtube.com/watch?v=m8wvCwnI_Qk
- ✅ **Instagram archived** (author, via browser, 2026-06-11 18:36 UTC): https://archive.ph/u3Vp2,
  verified live capture (caption + account visible, not a login wall). Plus:
- ✅ **Local evidence bundle, SHA-256 manifest + OpenTimestamps**: `evidence_manifest_sha256.json`
  hashes ig_reel.mp4 (8d47a84d…), ig_reel_metadata.json (platform timestamp inside),
  both transcripts, and the calendar frame; manifest digest stamped to the Bitcoin blockchain
  via both OpenTimestamps calendar pools 2026-06-11 (`evidence_manifest_ots_proofs.json`).
- Disclosed misses (author-reported, to be linked in final draft): $150k–$200k top targets
  (realized $124,824); 2026 bear-leg pattern calls = non-clock, claimed as no evidence.

## Data freeze
Bitstamp OHLC → 2026-06-10 · Coin Metrics → 2026-05-23 · macro (TV FRED mirror) → 2026-04.
