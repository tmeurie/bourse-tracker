"""Génération du rapport Excel : une feuille de synthèse + une feuille par ticker."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

from .indicators import add_indicators, summarize

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")
# En mise en forme conditionnelle, Excel lit bgColor : on renseigne les deux
GREEN_FILL = PatternFill("solid", fgColor="C6EFCE", bgColor="C6EFCE")
RED_FILL = PatternFill("solid", fgColor="FFC7CE", bgColor="FFC7CE")


def _style_header(ws: Worksheet, n_cols: int) -> None:
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=1, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")
    ws.freeze_panes = "A2"


def _autofit(ws: Worksheet) -> None:
    for col_cells in ws.columns:
        width = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        ws.column_dimensions[get_column_letter(col_cells[0].column)].width = min(width + 3, 30)


def _write_summary(ws: Worksheet, rows: list[dict]) -> None:
    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row[h] for h in headers])
    _style_header(ws, len(headers))

    last_row = len(rows) + 1
    # Vert si performance positive, rouge sinon
    perf_col = get_column_letter(headers.index("Performance (%)") + 1)
    rng = f"{perf_col}2:{perf_col}{last_row}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], fill=GREEN_FILL))
    ws.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL))
    _autofit(ws)


def _write_ticker_sheet(ws: Worksheet, df: pd.DataFrame) -> None:
    data = df.reset_index()
    ws.append(list(data.columns))
    for record in data.itertuples(index=False):
        ws.append([None if pd.isna(v) else v for v in record])
    _style_header(ws, len(data.columns))

    n = len(data) + 1
    for row in ws.iter_rows(min_row=2, max_row=n):
        row[0].number_format = "DD/MM/YYYY"
        for cell in row[1:]:
            cell.number_format = "#,##0.00"
    _autofit(ws)

    # Graphique : cours de clôture + moyennes mobiles
    chart = LineChart()
    chart.title = f"{ws.title} — Clôture et moyennes mobiles"
    chart.y_axis.title = "Prix"
    chart.x_axis.number_format = "mmm yy"
    chart.height, chart.width = 9, 22
    chart.legend.position = "r"
    chart.x_axis.tickLblSkip = 21  # environ une étiquette par mois de bourse
    chart.x_axis.tickMarkSkip = 21
    # Sans cela, les versions récentes d'Excel masquent les axes des graphiques openpyxl
    chart.x_axis.delete = False
    chart.y_axis.delete = False
    # Échelle adaptée aux prix (sinon l'axe part de 0 et la courbe est écrasée)
    low, high = data["Close"].min(), data["Close"].max()
    margin = (high - low) * 0.1 or abs(low) * 0.1 or 1
    chart.y_axis.scaling.min = round(max(low - margin, 0), 2)
    chart.y_axis.scaling.max = round(high + margin, 2)
    chart.y_axis.number_format = "#,##0"
    cols = list(data.columns)
    for name in ("Close", "MM20", "MM50"):
        idx = cols.index(name) + 1
        chart.add_data(Reference(ws, min_col=idx, min_row=1, max_row=n), titles_from_data=True)
    chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=n))
    ws.add_chart(chart, f"{get_column_letter(len(cols) + 2)}2")


def build_report(prices: dict[str, pd.DataFrame], output: str | Path) -> Path:
    """Construit le classeur Excel et retourne son chemin."""
    if not prices:
        raise ValueError("Aucune donnée à exporter")

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    summary_ws = wb.active
    summary_ws.title = "Synthèse"

    rows = []
    for ticker, raw in prices.items():
        df = add_indicators(raw)
        rows.append(summarize(ticker, df))
        # Titre de feuille Excel : 31 caractères max, sans caractères spéciaux
        title = "".join(c for c in ticker if c not in r"[]:*?/\\")[:31]
        _write_ticker_sheet(wb.create_sheet(title), df)

    _write_summary(summary_ws, rows)
    wb.save(output)
    return output
