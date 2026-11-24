# 📈 Bourse Tracker

[![CI](https://github.com/tmeurie/bourse-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/tmeurie/bourse-tracker/actions/workflows/ci.yml)

Outil en ligne de commande en **Python** qui récupère les cours de bourse (actions, indices, crypto) via Yahoo Finance, calcule des indicateurs financiers et génère un **rapport Excel** prêt à l'emploi.

## Fonctionnalités

- Récupération de l'historique de plusieurs actifs en une commande (`AAPL`, `MC.PA`, `BTC-USD`…)
- Calcul d'indicateurs :
  - rendement journalier
  - moyennes mobiles 20 et 50 jours
  - performance sur la période
  - volatilité annualisée
  - drawdown maximal (plus forte baisse depuis un sommet)
  - signal de tendance (croisement MM20 / MM50)
- Rapport Excel généré automatiquement :
  - une feuille **Synthèse** comparant tous les actifs (mise en forme conditionnelle vert/rouge)
  - une feuille par actif avec les données et un **graphique** cours + moyennes mobiles
- Gestion des erreurs : un ticker invalide est signalé sans bloquer les autres
- Tests unitaires (pytest), intégration continue (GitHub Actions) et image **Docker**

## Installation

```bash
git clone https://github.com/tmeurie/bourse-tracker.git
cd bourse-tracker
python -m venv .venv
# Windows : .venv\Scripts\activate   |   Linux/Mac : source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
# Tickers par défaut (Apple, Microsoft, LVMH, BNP Paribas, Bitcoin) sur 1 an
python -m bourse_tracker

# Tickers et période au choix
python -m bourse_tracker AAPL TSLA AIR.PA -p 6mo -o output/mon_rapport.xlsx
```

| Option | Description | Défaut |
|---|---|---|
| `tickers` | Symboles Yahoo Finance | `AAPL MSFT MC.PA BNP.PA BTC-USD` |
| `-p, --period` | `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `max` | `1y` |
| `-o, --output` | Chemin du fichier Excel | `output/rapport_<date>.xlsx` |
| `-v, --verbose` | Logs détaillés | — |

### Avec Docker

```bash
docker build -t bourse-tracker .
docker run --rm -v "$(pwd)/output:/app/output" bourse-tracker AAPL MSFT -p 6mo
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Les tests n'utilisent pas le réseau : les indicateurs et la génération Excel sont testés sur des données simulées.

## Structure

```
bourse_tracker/
├── fetch.py          # Récupération des données (yfinance)
├── indicators.py     # Calculs financiers (pandas)
├── excel_report.py   # Génération du classeur Excel (openpyxl)
└── cli.py            # Interface en ligne de commande (argparse)
tests/                # Tests unitaires (pytest)
Dockerfile            # Conteneurisation
.github/workflows/    # Intégration continue
```

## Technologies

Python 3.10+ · pandas · yfinance · openpyxl · pytest · Docker · GitHub Actions

## Avertissement

Projet pédagogique : les indicateurs ne constituent pas un conseil en investissement.
