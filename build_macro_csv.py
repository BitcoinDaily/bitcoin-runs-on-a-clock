"""
build_macro_csv.py — materialize the FRED series fetched via the TradingView desktop bridge
(FRED's own endpoints are bot-blocked from this network; TradingView mirrors the FRED feed).

Series captured 2026-06-10:
  FRED:M2SL  quarterly closes 2001Q3 -> 2026Q2(partial, =Apr2026), billions USD
  FRED:M2SL  monthly  closes 2018-01 -> 2026-04, billions USD
  FRED:T10Y2Y quarterly closes 2001Q3 -> 2026Q2(partial), percent

A quarterly bar's close = the series value in the LAST month of that quarter, so quarterly
closes are dated quarter-end month. Sanity assertions: monthly vs quarterly must agree on
every overlapping quarter-end.
"""
import numpy as np
import pandas as pd

M2_Q = [5355.1, 5440.5, 5502.0, 5553.3, 5662.3, 5779.4, 5868.4, 6002.2, 6079.7, 6073.8,
        6157.9, 6277.9, 6352.2, 6424.5, 6448.3, 6511.7, 6610.1, 6687.8, 6769.3, 6851.8,
        6952.4, 7080.1, 7168.2, 7287.8, 7413.0, 7483.9, 7670.0, 7743.9, 7872.4, 8204.7,
        8386.4, 8459.3, 8461.6, 8512.2, 8523.5, 8628.1, 8718.7, 8823.2, 8971.5, 9182.1,
        9551.5, 9683.9, 9853.9, 10021.6, 10226.1, 10484.1, 10583.8, 10703.3, 10862.0,
        11060.1, 11232.6, 11398.1, 11519.1, 11717.6, 11920.5, 12023.2, 12173.9, 12387.9,
        12661.8, 12852.5, 13054.9, 13234.9, 13463.6, 13580.5, 13745.1, 13881.7, 14012.7,
        14137.2, 14245.5, 14386.8, 14557.5, 14802.8, 15047.0, 15347.5, 16033.0, 18184.3,
        18602.5, 19115.7, 19873.2, 20477.1, 20981.0, 21498.8, 21786.8, 21651.2, 21536.5,
        21291.0, 20946.8, 20799.3, 20747.8, 20777.9, 20973.9, 21068.4, 21269.5, 21485.9,
        21693.7, 21938.8, 22170.3, 22353.5, 22686.4, 22804.5]

M2_M = [13900.3, 13949.3, 14012.7, 14035.9, 14092.4, 14137.2, 14174.6, 14223.2, 14245.5,
        14256.6, 14282.8, 14386.8, 14459.7, 14506.3, 14557.5, 14594.7, 14704.4, 14802.8,
        14886.8, 14974.4, 15047.0, 15184.1, 15296.0, 15347.5, 15427.1, 15493.4, 16033.0,
        17065.3, 17932.9, 18184.3, 18335.4, 18411.2, 18602.5, 18757.6, 18997.0, 19115.7,
        19379.0, 19641.8, 19873.2, 20175.4, 20459.0, 20477.1, 20633.3, 20840.7, 20981.0,
        21160.7, 21335.9, 21498.8, 21650.0, 21724.8, 21786.8, 21769.5, 21719.5, 21651.2,
        21652.8, 21638.2, 21536.5, 21461.5, 21406.5, 21291.0, 21279.4, 21242.9, 20946.8,
        20761.4, 20829.7, 20799.3, 20791.2, 20777.2, 20747.8, 20732.9, 20746.5, 20777.9,
        20843.9, 20927.4, 20973.9, 20959.7, 21020.7, 21068.4, 21095.3, 21186.8, 21269.5,
        21331.9, 21452.2, 21485.9, 21548.1, 21613.5, 21693.7, 21775.7, 21834.0, 21938.8,
        22020.0, 22086.9, 22170.3, 22245.1, 22277.4, 22353.5, 22429.3, 22627.0, 22686.4,
        22804.5]

T10Y2Y_Q = [1.74, 2.00, 1.70, 1.96, 1.91, 2.22, 2.32, 2.22, 2.46, 2.43, 2.26, 1.92, 1.51,
            1.16, 0.70, 0.28, 0.16, -0.02, 0.04, -0.01, -0.07, -0.11, 0.07, 0.16, 0.62,
            0.99, 1.83, 1.36, 1.85, 1.49, 1.90, 2.42, 2.36, 2.71, 2.82, 2.36, 2.11, 2.69,
            2.67, 2.73, 1.67, 1.64, 1.90, 1.34, 1.42, 1.53, 1.62, 2.16, 2.31, 2.66, 2.29,
            2.06, 1.94, 1.50, 1.38, 1.71, 1.42, 1.21, 1.05, 0.91, 0.83, 1.25, 1.13, 0.93,
            0.86, 0.51, 0.47, 0.33, 0.24, 0.21, 0.14, 0.25, 0.05, 0.34, 0.47, 0.50, 0.56,
            0.80, 1.58, 1.20, 1.24, 0.79, 0.04, 0.06, -0.39, -0.53, -0.58, -1.06, -0.44,
            -0.35, -0.39, -0.35, 0.15, 0.33, 0.34, 0.52, 0.56, 0.71, 0.51, 0.40]


def main():
    qe = pd.period_range("2001Q3", "2026Q2", freq="Q")
    assert len(qe) == len(M2_Q) == len(T10Y2Y_Q) == 100, (len(qe), len(M2_Q), len(T10Y2Y_Q))
    # quarterly close belongs to the quarter's last month (partial last quarter -> Apr 2026)
    qdates = [p.end_time.normalize() for p in qe]
    qdates[-1] = pd.Timestamp("2026-04-30")

    mdates = pd.date_range("2018-01-31", periods=len(M2_M), freq="ME")
    assert mdates[-1] == pd.Timestamp("2026-04-30")

    m2q = pd.Series(M2_Q, index=pd.DatetimeIndex(qdates), name="M2SL")
    m2m = pd.Series(M2_M, index=mdates, name="M2SL")
    # consistency: every overlapping quarter-end must agree exactly
    ov = m2q.index.intersection(m2m.index)
    assert len(ov) >= 30, f"only {len(ov)} overlaps"
    diff = (m2q.loc[ov] - m2m.loc[ov]).abs().max()
    assert diff < 0.05, f"monthly/quarterly mismatch {diff}"
    print(f"M2 monthly-vs-quarterly cross-check: {len(ov)} quarter-ends, max diff {diff:.3f}B  OK")

    m2 = pd.concat([m2q[~m2q.index.isin(m2m.index) & (m2q.index < m2m.index.min())], m2m])
    m2 = m2.sort_index()
    m2.rename_axis("date").to_csv("macro_m2.csv", header=["M2SL"])
    t = pd.Series(T10Y2Y_Q, index=pd.DatetimeIndex(qdates), name="T10Y2Y").sort_index()
    t.rename_axis("date").to_csv("macro_t10y2y.csv", header=["T10Y2Y"])

    yoy = m2.pct_change(4).iloc[-1] if False else (m2.iloc[-1] / m2[m2.index <= m2.index[-1] - pd.Timedelta(days=360)].iloc[-1] - 1)
    print(f"M2 merged: {len(m2)} obs {m2.index.min().date()} -> {m2.index.max().date()}, "
          f"latest {m2.iloc[-1]:,.1f}B (YoY ~{yoy*100:+.1f}%)")
    print(f"T10Y2Y: {len(t)} obs, latest {t.iloc[-1]:+.2f}")
    print("saved -> macro_m2.csv, macro_t10y2y.csv")


if __name__ == "__main__":
    main()
