# Bitcoin Runs on a Clock: Replication Package

Code, data, and audit trail for: **Molnar (2026), "Bitcoin Runs on a Clock: Why Every Price
Indicator Dies and the Halving Clock Doesn't"** (draft in `paper/`).

Every numerical claim in the manuscript maps to a line of script output. The mapping is indexed
in **`RESULTS_LOCK.md`**; the captured stdout of a full end-to-end re-run lives in **`audit/`**.
All stochastic procedures are seeded. Re-running reproduces the locked numbers exactly on
identically frozen data. The full core has additionally been reproduced end-to-end by an
independent analyst on independently pulled data (several rows bit-exact), and the manuscript
passed a multi-agent QA pass (60 findings, each adversarially verified against the artifacts
before correction).

## Quickstart

```
python -m pip install numpy pandas            # core (matplotlib for figures)
python pull_btc_ohlc.py                       # Bitstamp daily OHLC 2011-2026 (primary)
python pull_btc_daily.py                      # Coin Metrics close 2010-2026 (cross-check)
python pull_btc_metrics.py                    # Coin Metrics + MVRV + issuance (Puell)
python pull_eth_daily.py                      # ETH (replication asset)
python build_macro_csv.py                     # M2 + yield curve (values inline, self-checking)
# then any study script, e.g.:
python empirical_null_test.py                 # the spine: drawdown-process null, both constructions
```

Data freeze used by the locked results: Bitstamp → 2026-06-10, Coin Metrics → 2026-05-23.
Re-pulling moves nothing material, but bit-exact reproduction requires the freeze.

## Pipeline map (claim → script)

| Stage | Script | Manuscript |
|---|---|---|
| Causal power law + signal library | `pl_lib.py` | §4.1–4.2 |
| IC decay tables (descriptive) | `study_signals.py` | §5.4 |
| Nominal HAC cells | `ic_significance.py` | §4.3 |
| **Rotation null: per-epoch IC inference disqualified (p=0.21; NW size 0.17–0.33)** | `joint_replication_test.py` | §4.3 |
| BH-FDR (0/36) + uniform-null variant grid incl. hostile | `verify_hardening.py` | §4.3, §4.5 |
| Turn dating, cycle-caller hit/miss, extremes compression | `cycle_callers.py` | §3, §5.1–5.3 |
| **Drawdown-process null (spine): epoch-max 0/10,000; selection-symmetric 0.10–0.25%** | `empirical_null_test.py` | §4.5, §5.1 |
| Discrete trade structure | `pl_backtest.py` | §4.4 |
| Exposure Sharpe vs buy-and-hold | `exposure_study.py` | §5.4 |
| Coin Metrics + ETH replication | `replicate.py` | §5.5 |
| Parameter sweeps | `sweep_sensitivity.py` | §5.4 |
| Macro confounders (M2, yield curve) | `macro_study.py` | §5.6 |
| Satoshi Clock state + uniform permutation + prediction windows | `satoshi_clock.py` | §5.7, §8.2 |
| Figures | `paper/make_figures.py` | Figs 1–7 |
| PDF build (content-certified) | `paper/build_pdf.py` | . |

`satoshi_clock.pine` is the companion TradingView indicator: the same causal power-law corridor,
the CLOCK/SPRING readout, and the halving-cycle windows, drawn live on a chart (daily/weekly/
monthly). It is a visualization of the framework, not a backtested trading system (see §5.4).

## Real-time antecedent evidence (§8.1)

- YouTube (2025-01-11): archived at web.archive.org/web/20260611181109/…watch?v=m8wvCwnI_Qk;
  transcript `video_call_transcript.txt`.
- Instagram (2025-01-06): archived at archive.ph/u3Vp2. Redistributed in this repository:
  `ig_reel_transcript.txt` and `evidence_ig_calendar_oct20.png` ("Oct 20, 2025: SELL BITCOIN
  (18 Months POST HALVING)"). The raw video (`ig_reel.mp4`) and the platform metadata dump
  (`ig_reel_metadata.json`) are withheld here because the metadata payload embeds third-party
  commenter handles; both remain fixed by SHA-256 in the manifest below, and their public copy is
  the archive link above.
- Integrity: `evidence_manifest_sha256.json` (SHA-256 of every evidence file, including the two
  withheld above), its digest stamped to the Bitcoin blockchain via OpenTimestamps
  (`evidence_manifest_ots_proofs.json`).

## Honesty ledger

`RESULTS_LOCK.md` includes a **"Claims DOWNGRADED"** section, analytic envelopes and
flattering specifications that were retracted when empirical nulls disproved them are recorded
there permanently, so the package cannot silently regress to its prettier numbers. Headline
retraction: per-epoch IC significance (incl. an analytic 0.006 joint-replication claim) was
falsified by the dependence-preserving rotation null (empirical p = 0.21) and removed.

## Pre-registered predictions (falsifiers in manuscript §8.2)

- Cycle bottom window: **2026-10-05 → 2026-11-16** (weak test: bear durations are partly
  process-intrinsic).
- Next cycle top window: **2029-09-22 → 2029-10-13** (the sharp test).
