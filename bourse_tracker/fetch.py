"""Récupération des cours de bourse via l'API Yahoo Finance (bibliothèque yfinance)."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class FetchError(RuntimeError):
    """Levée quand aucune donnée n'a pu être récupérée pour un ticker."""


def fetch_prices(ticker: str, period: str = "1y") -> pd.DataFrame:
    """Télécharge l'historique journalier d'un ticker.

    Retourne un DataFrame indexé par date avec les colonnes
    Open, High, Low, Close, Volume.
    """
    import yfinance as yf  # import local : les tests n'ont pas besoin du réseau

    logger.info("Téléchargement de %s sur %s", ticker, period)
    df = yf.Ticker(ticker).history(period=period, auto_adjust=True)

    if df is None or df.empty:
        raise FetchError(f"Aucune donnée pour '{ticker}' (ticker invalide ?)")

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    # Excel ne gère pas les dates avec fuseau horaire
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df.index.name = "Date"
    return df


def fetch_many(tickers: list[str], period: str = "1y") -> dict[str, pd.DataFrame]:
    """Télécharge plusieurs tickers. Les tickers en erreur sont ignorés (avec un log)."""
    results: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        try:
            results[ticker] = fetch_prices(ticker, period)
        except Exception as exc:  # réseau, ticker inconnu, etc.
            logger.error("Échec pour %s : %s", ticker, exc)
    return results
