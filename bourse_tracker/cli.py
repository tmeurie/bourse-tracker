"""Point d'entrée en ligne de commande."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import date

from .excel_report import build_report
from .fetch import fetch_many

DEFAULT_TICKERS = ["AAPL", "MSFT", "MC.PA", "BNP.PA", "BTC-USD"]
VALID_PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="bourse-tracker",
        description="Récupère des cours de bourse et génère un rapport Excel.",
    )
    parser.add_argument(
        "tickers", nargs="*", default=DEFAULT_TICKERS,
        help=f"Symboles Yahoo Finance (défaut : {' '.join(DEFAULT_TICKERS)})",
    )
    parser.add_argument("-p", "--period", default="1y", choices=VALID_PERIODS, help="Période (défaut : 1y)")
    parser.add_argument(
        "-o", "--output", default=f"output/rapport_{date.today():%Y-%m-%d}.xlsx",
        help="Fichier Excel de sortie",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Logs détaillés")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    tickers = [t.upper() for t in args.tickers]
    prices = fetch_many(tickers, args.period)
    if not prices:
        logging.error("Aucun ticker n'a pu être récupéré.")
        return 1

    path = build_report(prices, args.output)
    logging.info("Rapport généré : %s (%d/%d tickers)", path, len(prices), len(tickers))
    return 0


if __name__ == "__main__":
    sys.exit(main())
