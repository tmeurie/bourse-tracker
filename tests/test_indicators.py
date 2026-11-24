import pandas as pd
import pytest

from bourse_tracker.indicators import (
    add_indicators,
    annualized_volatility,
    max_drawdown,
    summarize,
    total_return,
    trend_signal,
)


def make_prices(values):
    idx = pd.date_range("2025-01-01", periods=len(values), freq="B", name="Date")
    return pd.DataFrame(
        {"Open": values, "High": values, "Low": values, "Close": values, "Volume": 1000},
        index=idx,
    )


def test_total_return():
    close = pd.Series([100.0, 110.0, 150.0])
    assert total_return(close) == pytest.approx(50.0)


def test_max_drawdown():
    # Sommet à 200 puis chute à 100 -> -50 %
    close = pd.Series([100.0, 200.0, 150.0, 100.0, 180.0])
    assert max_drawdown(close) == pytest.approx(-50.0)


def test_max_drawdown_only_rising():
    assert max_drawdown(pd.Series([1.0, 2.0, 3.0])) == 0


def test_volatility_constant_price_is_zero():
    assert annualized_volatility(pd.Series([10.0] * 30)) == 0


def test_volatility_too_short():
    assert annualized_volatility(pd.Series([10.0, 11.0])) == 0.0


def test_add_indicators_columns_and_moving_average():
    df = add_indicators(make_prices([float(i) for i in range(1, 61)]))
    assert {"Rendement (%)", "MM20", "MM50"} <= set(df.columns)
    # MM20 au 20e jour = moyenne de 1..20 = 10.5
    assert df["MM20"].iloc[19] == pytest.approx(10.5)
    assert pd.isna(df["MM50"].iloc[48])


def test_trend_signal():
    rising = add_indicators(make_prices([float(i) for i in range(1, 61)]))
    falling = add_indicators(make_prices([float(i) for i in range(60, 0, -1)]))
    short = add_indicators(make_prices([1.0, 2.0, 3.0]))
    assert trend_signal(rising) == "HAUSSIER"
    assert trend_signal(falling) == "BAISSIER"
    assert trend_signal(short) == "N/A"


def test_summarize_keys():
    df = add_indicators(make_prices([float(i) for i in range(1, 61)]))
    s = summarize("TEST", df)
    assert s["Ticker"] == "TEST"
    assert s["Dernier cours"] == 60.0
    assert s["Performance (%)"] == pytest.approx(5900.0)
