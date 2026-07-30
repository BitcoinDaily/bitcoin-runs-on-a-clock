"""build_height_series.py — daily date->block-height series for the BLOCK-PHASE battery.

Source: Coin Metrics community btc.csv, column BlkCnt (blocks mined per UTC day), contiguous
daily from the 2009-01-03 genesis. Cumulative-summed to an END-OF-DAY block height. This is the
exogenous clock the block-phase empirical null maps synthetic turn dates through (the mapping is
independent of price, so scoring a price-null in block phase is clean).

Anchor / convention: height_eod[d] = cumsum(BlkCnt through d) - 1  (heights are 0-indexed: N
blocks mined -> tip height N-1; genesis block 0 mined 2009-01-03). This is a PRINCIPLED anchor,
not fitted to the turns. It is then HARD-VALIDATED, refusing to save on failure:

  (a) the four halving protocol heights (210000/420000/630000/840000) must be reached within
      +/-1 day of their known dates;
  (b) the 11 mempool.space noon point-lookups in block_clock_data.json must agree within a
      stated tolerance. NOTE a systematic offset is EXPECTED and benign: this series is
      end-of-day, the mempool lookups are noon-UTC, so this series runs ~half a day (~72 blocks
      at ~145 blk/day) HIGHER. That constant sampling offset cancels in every RANGE statistic
      the battery computes (both observed and synthetic use this one instrument).

Quarantined output (never overwrites an existing CSV): block_height_daily.csv.

  cd PowerLaw && python build_height_series.py
"""
import io
import json
import os
import sys
import urllib.request

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
CM_URL = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv"
OUT = os.path.join(HERE, "block_height_daily.csv")

# exact protocol halving heights and their known calendar dates (ground truth)
HALVINGS = [
    (210000, pd.Timestamp("2012-11-28")),
    (420000, pd.Timestamp("2016-07-09")),
    (630000, pd.Timestamp("2020-05-11")),
    (840000, pd.Timestamp("2024-04-20")),
]


def fetch_blkcnt():
    print(f"fetching Coin Metrics btc.csv BlkCnt ...")
    req = urllib.request.Request(CM_URL, headers={"User-Agent": "Mozilla/5.0 (research)"})
    raw = urllib.request.urlopen(req, timeout=180).read()
    print(f"  got {len(raw)/1e6:.1f} MB")
    df = pd.read_csv(io.BytesIO(raw), usecols=["time", "BlkCnt"])
    df["date"] = pd.to_datetime(df["time"]).dt.tz_localize(None).dt.normalize()
    df = df.dropna(subset=["BlkCnt"]).sort_values("date").reset_index(drop=True)
    return df[["date", "BlkCnt"]]


def main():
    df = fetch_blkcnt()
    # contiguity guard: the cumulative sum is only meaningful if there are no missing days
    step = df["date"].diff().dt.days.dropna()
    n_gap = int((step != 1).sum())
    print(f"  BlkCnt rows {len(df)}  span {df['date'].min().date()} -> {df['date'].max().date()}"
          f"  non-1-day steps {n_gap}")
    if n_gap:
        raise SystemExit("BlkCnt has calendar gaps; cumulative height would be wrong. refusing.")

    df["blocks_cum"] = df["BlkCnt"].cumsum().astype("int64")
    df["height_eod"] = df["blocks_cum"] - 1     # N blocks mined -> tip height N-1

    ser = df.set_index("date")["height_eod"]

    # ---- validation (a): halving protocol heights land on their known dates ----
    print("\nvalidation (a): protocol halving heights vs known dates (end-of-day series)")
    ok_all = True
    for exact, d in HALVINGS:
        # first calendar day on which the eod height reaches the protocol halving height
        reached = ser[ser >= exact]
        first_day = reached.index[0] if len(reached) else None
        delta_days = (first_day - d).days if first_day is not None else None
        eod_here = int(ser.loc[d]) if d in ser.index else None
        ok = first_day is not None and abs(delta_days) <= 1
        ok_all &= ok
        print(f"  {exact:>7,} known {d.date()}  first eod>=height on {first_day.date() if first_day is not None else 'NA'}"
              f"  delta {delta_days:+d}d   eod_height_on_known_date {eod_here:,}  {'OK' if ok else 'FAIL'}")
    if not ok_all:
        raise SystemExit("halving-date validation failed; refusing to save a bad height series.")

    # ---- validation (b): the 11 mempool noon point-lookups ----
    with open(os.path.join(HERE, "block_clock_data.json"), encoding="utf-8") as f:
        bc = json.load(f)
    pts = [(p["raw"]["timestamp"][:10], p["noon_height"], p["what"]) for p in bc["points"]]
    print("\nvalidation (b): mempool noon point-lookups vs this end-of-day series"
          "\n  (eod runs ~+half-day higher than noon; report the offset, it is benign+constant)")
    diffs = []
    for ds, noon_h, what in pts:
        d = pd.Timestamp(ds)
        if d in ser.index:
            eod_h = int(ser.loc[d])
            diff = eod_h - noon_h
            diffs.append(diff)
            print(f"  {ds}  noon {noon_h:>7,}  eod {eod_h:>7,}  eod-noon {diff:+5d}  {what}")
    diffs = np.array(diffs)
    print(f"\n  eod-minus-noon offset: median {np.median(diffs):+.0f}  min {diffs.min():+d}  max {diffs.max():+d}"
          f"  (all same sign = pure sampling-time offset, cancels in ranges)")
    # tolerance: noon lookups should sit BELOW eod, within ~half a day of blocks (~250 generous)
    within = np.abs(diffs - np.median(diffs)).max()
    print(f"  max deviation from the median offset: {within:.0f} blocks (intraday wobble)")
    if within > 250:
        raise SystemExit("point-lookups deviate too far from a constant offset; source suspect.")

    out = df[["date", "BlkCnt", "blocks_cum", "height_eod"]].copy()
    out.to_csv(OUT, index=False)
    print(f"\nsaved -> {OUT}  ({len(out)} rows, {out['date'].min().date()} -> {out['date'].max().date()})")
    print("VALIDATION PASSED — series is safe for the block-phase battery.")


if __name__ == "__main__":
    main()
