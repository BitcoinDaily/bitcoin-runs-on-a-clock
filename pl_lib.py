"""
pl_lib.py — power-law + comparator signals for Bitcoin, all CAUSAL (no look-ahead).

The whole study hinges on the power-law trend being fit *causally* — at each day t the
parameters (A, n in  price ~ A * t^n) are estimated using ONLY data up to that day. This is the
single thing that separates an honest result from the discredited Stock-to-Flow / full-sample-fit
crowd, whose "trend line" is drawn through the very future they then claim to predict.

Signals produced (all daily, all causal):
  pl_z    : z-score of log-residual from the causal power-law fit (price vs A*t^n)
  rsi     : Wilder RSI(14) on daily close
  mayer_z : z-score of log Mayer Multiple  ln(price / SMA200)  (the classic BTC MA-distance osc.)

Genesis = 2009-01-03 (Bitcoin block 0). t = days since genesis.
"""
import numpy as np
import pandas as pd

GENESIS = pd.Timestamp("2009-01-03")

# Halving dates -> epoch boundaries (each epoch is the cycle that halving kicks off).
HALVINGS = {
    1: pd.Timestamp("2012-11-28"),
    2: pd.Timestamp("2016-07-09"),
    3: pd.Timestamp("2020-05-11"),
    4: pd.Timestamp("2024-04-20"),
}


def load_prices(path="btc_ohlc_daily.csv", genesis=GENESIS):
    """Daily OHLC DataFrame indexed by date, columns o,h,l,c,v (+ t = days since genesis)."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df["t"] = (df.index - genesis).days.astype(float)
    return df


def load_close_csv(path, genesis=GENESIS, price_col="close"):
    """Close-only daily series (e.g. Coin Metrics PriceUSD) shaped like load_prices output.
    o/h/l are set equal to c so signal-building works; intrabar backtests must NOT be run on
    this (no real range) — it is for the IC and exposure studies, which use closes only."""
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    df = df[~df.index.duplicated(keep="first")]
    df["c"] = df[price_col].astype(float)
    df = df[df["c"] > 0]
    df["o"] = df["c"]; df["h"] = df["c"]; df["l"] = df["c"]; df["v"] = np.nan
    df["t"] = (df.index - genesis).days.astype(float)
    return df[["o", "h", "l", "c", "v", "t"]]


def epoch_of(dates):
    """Map each date to its halving epoch (1..4); 0 = pre-first-halving."""
    dates = pd.DatetimeIndex(dates)
    ep = np.zeros(len(dates), int)
    for e, h in HALVINGS.items():
        ep[dates >= h] = e
    return ep


# --------------------------------------------------------------------------------------
# Causal expanding-window power-law fit  (O(N) via running sums)
# --------------------------------------------------------------------------------------
def causal_powerlaw(df, min_obs=365):
    """Return (slope n_t, intercept lnA_t, log-residual r_t) where the fit at each day uses only
    days up to and including that day. Fit is OLS of y=ln(price) on x=ln(t).

    Running sums make this exact and O(N): at day i the closed-form OLS slope/intercept use
    Sx,Sy,Sxx,Sxy,count over [0..i]. The residual r_i = y_i - (lnA_i + n_i * x_i) is therefore
    a fully causal "how far is price above/below its own to-date trend" measure.
    """
    x = np.log(df["t"].to_numpy())
    y = np.log(df["c"].to_numpy())
    N = len(x)
    n_t = np.full(N, np.nan)
    lnA_t = np.full(N, np.nan)
    r_t = np.full(N, np.nan)
    Sx = Sy = Sxx = Sxy = 0.0
    for i in range(N):
        Sx += x[i]; Sy += y[i]; Sxx += x[i]*x[i]; Sxy += x[i]*y[i]
        k = i + 1
        if k >= min_obs:
            denom = k*Sxx - Sx*Sx
            if denom > 0:
                slope = (k*Sxy - Sx*Sy) / denom
                intercept = (Sy - slope*Sx) / k
                n_t[i] = slope
                lnA_t[i] = intercept
                r_t[i] = y[i] - (intercept + slope*x[i])
    return n_t, lnA_t, r_t


def expanding_z(r, min_obs=180):
    """Causal z-score of a series: (r_i - expanding_mean) / expanding_std, using only [0..i]."""
    s = pd.Series(r)
    mu = s.expanding(min_periods=min_obs).mean()
    sd = s.expanding(min_periods=min_obs).std(ddof=0)
    return ((s - mu) / sd).to_numpy()


def wilder_rsi(close, n=14):
    """Wilder RSI on close. Causal."""
    c = np.asarray(close, float)
    d = np.diff(c, prepend=c[0])
    up = np.where(d > 0, d, 0.0); dn = np.where(d < 0, -d, 0.0)
    ru = np.full(len(c), np.nan); rd = np.full(len(c), np.nan)
    if len(c) <= n:
        return np.full(len(c), np.nan)
    ru[n] = up[1:n+1].mean(); rd[n] = dn[1:n+1].mean()
    a = 1.0/n
    for i in range(n+1, len(c)):
        ru[i] = a*up[i] + (1-a)*ru[i-1]
        rd[i] = a*dn[i] + (1-a)*rd[i-1]
    rs = ru / np.where(rd == 0, np.nan, rd)
    rsi = 100 - 100/(1+rs)
    rsi[rd == 0] = 100.0
    return rsi


def sma(x, n):
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()


def build_signals(df):
    """Attach all causal signals to df: pl_z, rsi, mayer_z (+ raw pl residual, fit params)."""
    n_t, lnA_t, r_t = causal_powerlaw(df)
    df = df.copy()
    df["pl_n"] = n_t
    df["pl_resid"] = r_t
    df["pl_z"] = expanding_z(r_t)
    df["rsi"] = wilder_rsi(df["c"].to_numpy(), 14)
    mayer = np.log(df["c"].to_numpy() / sma(df["c"].to_numpy(), 200))
    df["mayer_z"] = expanding_z(mayer)
    df["epoch"] = epoch_of(df.index)
    return df
