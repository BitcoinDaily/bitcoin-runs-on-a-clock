# RESULTS_LOCK, every load-bearing manuscript number → script → captured output

> **REVISION v1.6 (2026-07-21):** added the block-clock analysis (§3 Data note, §5.9, §8.2 block-height
> windows, Appendix A scripts). New review PDF `paper/Bitcoin_Runs_on_a_Clock_Molnar_2026_draft.pdf`
> sha256 **fc354ae01a1b**, 32 pages, content-certified **42/42**. Ledger `main.tex` re-built + certified
> 42/42, abstract 199 words. Mappings in the "Block-clock revision" section below. STAGED for founder
> review, not uploaded/pushed/submitted.

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

## Block-clock revision (manuscript v1.6, 2026-07-21) — §3 Data note + §5.9 + §8.2

New load-bearing numbers, all reproducing from the seeded block-phase scripts (SEED=31 for the null,
rng 7/3/5 for placebos, matching the day-clock originals). Height series from `build_height_series.py`.
Captured stdout: `audit/block_phase_null.out`, `audit/block_phase_tests.out`, `audit/build_height_series.out`.

| Manuscript claim | Value | Script | Output |
|---|---|---|---|
| Height series validation (§3) | CM BlkCnt genesis→2026-05-23, contiguous no gaps; 4 halvings reached within ±1d; 11 mempool lookups a constant +62..+103 (median +75) above end-of-day | build_height_series.py | audit/build_height_series.out |
| **Block tops null (§5.9)** | epoch-max **0/10,000** (= day 0/10,000); selection-symmetric **3/10,000** (day 11/10,000) | block_phase_null.py | audit/block_phase_null.out |
| **Block bottoms PARTIAL rescue (§5.9)** | after-halving phase-range day **171/10,000 (1.7%)** → block **16/10,000 (0.16%)**; conditional on structure **3.7%→0.3%**; top→bottom LAG NOT sharpened (day 0.42% / block 1.11%) = independent anchoring | block_phase_null.py | audit/block_phase_null.out |
| **Bottom gap-stat STILL DEMOTED (§5.9)** | top→bottom duration reproduced **~40%** (day 4054/10,000); the block after-halving result is a PARTIAL rescue, NOT a reversal of the §4.5 demotion | block_phase_null.py | audit/block_phase_null.out |
| **Block E1 reconciliation (§5.9)** | 2013-top ratio **0.693 (day) → 0.801 (block)**; early chain 170 vs 147 blk/day (+15%); hostile 4-top null **8/10,000 (day) → 3/10,000 (block)** | block_phase_null.py, block_phase_tests.py | audit/block_phase_null.out, audit/block_phase_tests.out |
| **Block placebo clocks (§5.9)** | halving 1,723 / election 12,775 / fixed-cal 209,158; random-OFFSET degeneracy **P=98.5%** (period not phase, dissolves anchor question); random-PERIOD P(≤1,723)=**0.9%** | block_phase_tests.py | audit/block_phase_tests.out |
| **Block LOSSES reported (§5.9)** | seasonality overlay **0.69 (block) < 0.72 (day)**; vol clock placebo **P=0.40 (block) vs 0.19 (day)** = still a MISS, worse; return-by-phase flip lands on 77,901..79,596-blk top band | block_phase_tests.py | audit/block_phase_tests.out |
| **Block-height predictions (§8.2)** | 2026 bottom band **968,910..973,934** (= 840,000 + 128,910..133,934); 2029 top band **1,127,901..1,129,596** (= 1,050,000 + 77,901..79,596); logged 2026-07-21 pre-window | block_clock.py (mempool noon lookups) | block_clock_data.json |

**INSTRUMENT NOTE.** Two consistent instruments. The manuscript phase BANDS (77,901..79,596 tops;
128,910..133,934 bottoms; ranges 1,695 / 5,024) are the mempool.space noon point-lookups
(`block_clock_data.json`, ground truth). The NULL p-values are scored by `block_phase_null.py` against
the mechanical daily-series ranges (1,723 tops / 5,220 bottoms), which equal the ground truth within
end-of-day sampling (+28 / +196 blocks); the deterministic 0/10,000 holds a fortiori at the tighter band.

**PRESERVED DEMOTION.** The §4.5 / DOWNGRADED-item-0 bottom-timing demotion STANDS. The block
after-halving result (0.16%) is a phase-based PARTIAL rescue on n=3, framed in §5.9 as a weak prior, and
does NOT reinstate the demoted gap/duration statistic (still ~40%). §5.9 states this explicitly.

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

## Submission packaging (venue phase — mapping unchanged, logged so nothing regresses silently)
- **SSRN**: live, abstract 6977940 (revised to the 8d764e1e PDF). **arXiv q-fin.ST**: parked
  (Challet declined endorsement; Garcia-Medina no reply).
- **Ledger** (ledgerjournal.org, Univ. of Pittsburgh) built 2026-07-17 in `submission/ledger/`
  via `submission/build_ledger.py` (deterministic md→Ledger-class LaTeX; reuses the certified
  `build_latex.py` body conversion, so §1–§9 + appendix prose is byte-identical to the arXiv build).
  **Source content-certification: 42/42 LOCK numbers present** in `submission/ledger/main.tex`
  (`python submission/certify.py submission/ledger/main.tex`); 0 em-dashes; 19 distinct cited keys
  == 19 bib keys (raw \cite count 21 = newey1987 cited in 3 blocks, pre-existing, correct). **Not
  compiled locally** (no TeX toolchain on this machine) → final PDF is an Overleaf step, then
  re-certify the compiled PDF. (v1.6: +8 block-clock checks, 34→42.)
- **Body prose, findings, numbers, tables: UNCHANGED.** Venue-only adaptations, none touching a
  claim's calibration: (a) abstract compressed to a **194-word** Ledger-cap version (full ~647-word
  abstract preserved verbatim in a `main.tex` comment; the compression mirrors this LOCK —
  retrospective regularity, tops = the sharp test, IC descriptive, no upgraded verbs — and is a
  **decision point flagged for author sign-off**, not a silent edit; v1.6 re-drafted to 199 words
  with a block-clock clause added); (b) new front-matter prose
  (Acknowledgements / Author Contributions / Conflict of Interest), the CoI mirroring §8.1's
  disclosure; (c) numeric superscript `\cite` replacing natbib; (d) keywords with "Bitcoin" removed
  per Ledger rule; (e) bib key `santostasi2024`→`santostasi2026` (mechanical; entry already carried
  the peer-reviewed Santostasi & Perrenod 2026 content); (f) the promised public-repo URL filled into
  Appendix A.
- **Open decision for the founder:** Ledger word-count guidance is self-contradictory (live page
  ≤10,000 vs 2015 AuthorGuide.pdf ≤4,000). Body now **≈10,115 words** (was ≈9,200; +~900 for the
  §5.9 block clock, well under the +1,000 target). **No content was cut.** The §5.9 addition now
  nudges the body just over the 10,000 live-page number; if Ledger enforces either limit, trimming
  or moving §5.9 to an appendix is a science-side call for research-extender, not a packaging edit.
