"""Indicateurs financiers calculés à partir d'une série de cours de clôture."""

from __future__ import annotations

import math

import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute le rendement journalier et les moyennes mobiles 20 et 50 jours."""
    out = df.copy()
    out["Rendement (%)"] = out["Close"].pct_change() * 100
    out["MM20"] = out["Close"].rolling(window=20).mean()
    out["MM50"] = out["Close"].rolling(window=50).mean()
    return out


def total_return(close: pd.Series) -> float:
    """Performance sur la période, en %."""
    return (close.iloc[-1] / close.iloc[0] - 1) * 100


def annualized_volatility(close: pd.Series) -> float:
    """Volatilité annualisée des rendements journaliers, en %."""
    daily = close.pct_change().dropna()
    if len(daily) < 2:
        return 0.0
    return daily.std() * math.sqrt(TRADING_DAYS_PER_YEAR) * 100


def max_drawdown(close: pd.Series) -> float:
    """Plus forte baisse depuis un sommet, en % (valeur négative ou nulle)."""
    running_max = close.cummax()
    drawdowns = close / running_max - 1
    return drawdowns.min() * 100


def trend_signal(df: pd.DataFrame) -> str:
    """Signal simple : HAUSSIER si MM20 > MM50, BAISSIER sinon."""
    last = df.iloc[-1]
    if pd.isna(last.get("MM20")) or pd.isna(last.get("MM50")):
        return "N/A"
    return "HAUSSIER" if last["MM20"] > last["MM50"] else "BAISSIER"


def summarize(ticker: str, df: pd.DataFrame) -> dict:
    """Résumé d'un ticker pour la feuille de synthèse."""
    close = df["Close"]
    return {
        "Ticker": ticker,
        "Dernier cours": round(close.iloc[-1], 2),
        "Plus haut": round(close.max(), 2),
        "Plus bas": round(close.min(), 2),
        "Performance (%)": round(total_return(close), 2),
        "Volatilité ann. (%)": round(annualized_volatility(close), 2),
        "Drawdown max (%)": round(max_drawdown(close), 2),
        "Tendance": trend_signal(df),
    }
