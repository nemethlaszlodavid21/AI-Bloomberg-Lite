import numpy as np
import pandas as pd


def napi_hozamok_szamitas(tortenet):

    if tortenet is None or tortenet.empty:
        return pd.Series(dtype=float)

    if "Daily Return" in tortenet.columns:

        return (
            pd.to_numeric(
                tortenet["Daily Return"],
                errors="coerce"
            )
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
            .dropna()
        )

    if "Portfolio" not in tortenet.columns:
        return pd.Series(dtype=float)

    return (
        tortenet["Portfolio"]
        .pct_change()
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .dropna()
    )


def annualizalt_volatilitas(napi_hozamok):

    if napi_hozamok is None or len(napi_hozamok) < 2:
        return None

    szoras = napi_hozamok.std()

    if pd.isna(szoras):
        return None

    return szoras * np.sqrt(252) * 100


def _hozam_index(tortenet):

    napi_hozamok = napi_hozamok_szamitas(
        tortenet
    )

    if napi_hozamok.empty:
        return pd.Series(dtype=float)

    return (
        (1.0 + napi_hozamok)
        .cumprod()
        * 100
    )


def max_drawdown_szamitas(tortenet):

    hozam_index = _hozam_index(
        tortenet
    )

    if hozam_index.empty:
        return None

    running_max = hozam_index.cummax()

    drawdown = (
        hozam_index
        / running_max
        - 1
    )

    return drawdown.min() * 100


def drawdown_idosor(tortenet):

    hozam_index = _hozam_index(
        tortenet
    )

    if hozam_index.empty:
        return pd.DataFrame()

    running_max = hozam_index.cummax()

    drawdown = (
        hozam_index
        / running_max
        - 1
    ) * 100

    return pd.DataFrame(
        {
            "Drawdown %": drawdown
        }
    )


def sharpe_ratio_szamitas(
    napi_hozamok,
    kockazatmentes_hozam=0.0
):

    if napi_hozamok is None or len(napi_hozamok) < 2:
        return None

    napi_rf = (
        (1 + float(kockazatmentes_hozam) / 100)
        ** (1 / 252)
        - 1
    )

    excess_return = (
        napi_hozamok
        - napi_rf
    )

    szoras = excess_return.std()

    if pd.isna(szoras) or szoras == 0:
        return None

    return (
        excess_return.mean()
        / szoras
        * np.sqrt(252)
    )


def sortino_ratio_szamitas(
    napi_hozamok,
    kockazatmentes_hozam=0.0
):

    if napi_hozamok is None or napi_hozamok.empty:
        return None

    napi_rf = (
        (1 + float(kockazatmentes_hozam) / 100)
        ** (1 / 252)
        - 1
    )

    excess_return = (
        napi_hozamok
        - napi_rf
    )

    downside = np.minimum(
        excess_return,
        0.0
    )

    downside_deviation = np.sqrt(
        np.mean(
            np.square(
                downside
            )
        )
    )

    if (
        pd.isna(downside_deviation)
        or downside_deviation == 0
    ):
        return None

    return (
        excess_return.mean()
        / downside_deviation
        * np.sqrt(252)
    )


def historikus_var_95(napi_hozamok):

    if napi_hozamok is None or napi_hozamok.empty:
        return None

    percentile = np.percentile(
        napi_hozamok,
        5
    )

    return percentile * 100


def beta_szamitas(portfolio_benchmark):

    if portfolio_benchmark is None or portfolio_benchmark.empty:
        return None

    if (
        "Portfolio" not in portfolio_benchmark.columns
        or "S&P 500" not in portfolio_benchmark.columns
    ):
        return None

    adatok = (
        portfolio_benchmark[
            ["Portfolio", "S&P 500"]
        ]
        .dropna()
    )

    if len(adatok) < 3:
        return None

    portfolio_returns = (
        adatok["Portfolio"]
        .pct_change()
    )

    benchmark_returns = (
        adatok["S&P 500"]
        .pct_change()
    )

    returnok = pd.DataFrame(
        {
            "Portfolio": portfolio_returns,
            "Benchmark": benchmark_returns
        }
    ).dropna()

    if returnok.empty:
        return None

    benchmark_variancia = (
        returnok["Benchmark"]
        .var()
    )

    if (
        pd.isna(benchmark_variancia)
        or benchmark_variancia == 0
    ):
        return None

    covariance = (
        returnok["Portfolio"]
        .cov(
            returnok["Benchmark"]
        )
    )

    return (
        covariance
        / benchmark_variancia
    )


def risk_analytics_szamitas(
    tortenet,
    benchmark_adatok,
    portfolio_ertek,
    kockazatmentes_hozam=0.0
):

    napi_hozamok = (
        napi_hozamok_szamitas(
            tortenet
        )
    )

    volatilitas = annualizalt_volatilitas(
        napi_hozamok
    )

    max_drawdown = max_drawdown_szamitas(
        tortenet
    )

    sharpe = sharpe_ratio_szamitas(
        napi_hozamok,
        kockazatmentes_hozam
    )

    sortino = sortino_ratio_szamitas(
        napi_hozamok,
        kockazatmentes_hozam
    )

    var_95_szazalek = historikus_var_95(
        napi_hozamok
    )

    beta = beta_szamitas(
        benchmark_adatok
    )

    if (
        var_95_szazalek is not None
        and portfolio_ertek is not None
    ):

        var_95_huf = (
            float(portfolio_ertek)
            * abs(var_95_szazalek)
            / 100
        )

    else:
        var_95_huf = None

    return {
        "Volatilitás %": volatilitas,
        "Max Drawdown %": max_drawdown,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Beta": beta,
        "VaR 95% %": var_95_szazalek,
        "VaR 95% HUF": var_95_huf
    }
