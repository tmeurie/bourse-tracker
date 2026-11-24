import pandas as pd
import pytest
from openpyxl import load_workbook

from bourse_tracker.excel_report import build_report


def make_prices(n=60, start=100.0):
    idx = pd.date_range("2025-01-01", periods=n, freq="B", name="Date")
    values = [start + i for i in range(n)]
    return pd.DataFrame(
        {"Open": values, "High": values, "Low": values, "Close": values, "Volume": 1000},
        index=idx,
    )


def test_build_report_creates_sheets(tmp_path):
    out = build_report({"AAA": make_prices(), "BBB": make_prices(start=50)}, tmp_path / "r.xlsx")
    wb = load_workbook(out)
    assert wb.sheetnames == ["Synthèse", "AAA", "BBB"]

    synth = wb["Synthèse"]
    assert synth["A1"].value == "Ticker"
    assert synth["A2"].value == "AAA"
    assert synth["A3"].value == "BBB"

    sheet = wb["AAA"]
    assert sheet.max_row == 61  # en-tête + 60 jours
    assert len(sheet._charts) == 1


def test_build_report_empty_raises(tmp_path):
    with pytest.raises(ValueError):
        build_report({}, tmp_path / "r.xlsx")
