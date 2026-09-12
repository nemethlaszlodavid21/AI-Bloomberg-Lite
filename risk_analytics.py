import numpy as np
import pandas as pd


def napi_hozamok_szamitas(tortenet):

    if tortenet is None:
        return pd.Series(dtype=float)

    if tortenet.empty:
        return pd.Series(dtype=float)

    if "Portfolio" not in tortenet.columns:
        return pd.Series(dtype=float)

    napi_hozamok = (
        tortenet["Portfolio"]
        .pct_change()
        .dropna()
    )

    return napi_hozamok


def annualizalt_volatilitas(
    napi_hozamok
):

    if napi_hozamok.empty:
        return None

    return (
        napi_hozamok.std()
        * np.sqrt(252)
        * 100
    )


def max_drawdown_szamitas(
    tortenet
):

    if tortenet is None:
        return None

    if tortenet.empty:
        return None

    if "Portfolio" not in tortenet.columns:
        return None

    portfolio_ertek = (
        tortenet["Portfolio"]
        .dropna()
    )

    if portfolio_ertek.empty:
        return None

    running_max = (
        portfolio_ertek
        .cummax()
    )

    drawdown = (
        portfolio_ertek
        / running_max
        - 1
    )

    return (
        drawdown.min()
        * 100
    )


def drawdown_idosor(
    tortenet
):

    if tortenet is None:
        return pd.DataFrame()

    if tortenet.empty:
        return pd.DataFrame()

    if "Portfolio" not in tortenet.columns:
        return pd.DataFrame()

    portfolio_ertek = (
        tortenet["Portfolio"]
        .dropna()
    )

    running_max = (
        portfolio_ertek
        .cummax()
    )

    drawdown = (
        portfolio_ertek
        / running_max
        - 1
    ) * 100

    eredmeny = pd.DataFrame(
        {
            "Drawdown %": drawdown
        }
    )

    return eredmeny


def sharpe_ratio_szamitas(
    napi_hozamok,
    kockazatmentes_hozam=0.0
):

    if napi_hozamok.empty:
        return None

    napi_rf = (
        kockazatmentes_hozam
        / 100
        / 252
    )

    excess_return = (
        napi_hozamok
        - napi_rf
    )

    szoras = excess_return.std()

    if szoras == 0:
        return None

    sharpe = (
        excess_return.mean()
        / szoras
        * np.sqrt(252)
    )

    return sharpe


def sortino_ratio_szamitas(
    napi_hozamok,
    kockazatmentes_hozam=0.0
):

    if napi_hozamok.empty:
        return None

    napi_rf = (
        kockazatmentes_hozam
        / 100
        / 252
    )

    excess_return = (
        napi_hozamok
        - napi_rf
    )

    negativ_hozamok = (
        excess_return[
            excess_return < 0
        ]
    )

    if negativ_hozamok.empty:
        return None

    downside_deviation = (
        negativ_hozamok.std()
    )

    if downside_deviation == 0:
        return None

    sortino = (
        excess_return.mean()
        / downside_deviation
        * np.sqrt(252)
    )

    return sortino


def historikus_var_95(
    napi_hozamok
):

    if napi_hozamok.empty:
        return None

    percentile = np.percentile(
        napi_hozamok,
        5
    )

    return (
        percentile
        * 100
    )


def beta_szamitas(
    portfolio_benchmark
):

    if portfolio_benchmark is None:
        return None

    if portfolio_benchmark.empty:
        return None

    if (
        "Portfolio"
        not in portfolio_benchmark.columns
        or
        "S&P 500"
        not in portfolio_benchmark.columns
    ):
        return None

    adatok = (
        portfolio_benchmark[
            [
                "Portfolio",
                "S&P 500"
            ]
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

    if benchmark_variancia == 0:
        return None

    covariance = (
        returnok["Portfolio"]
        .cov(
            returnok["Benchmark"]
        )
    )

    beta = (
        covariance
        / benchmark_variancia
    )

    return beta


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

    volatilitas = (
        annualizalt_volatilitas(
            napi_hozamok
        )
    )

    max_drawdown = (
        max_drawdown_szamitas(
            tortenet
        )
    )

    sharpe = (
        sharpe_ratio_szamitas(
            napi_hozamok,
            kockazatmentes_hozam
        )
    )

    sortino = (
        sortino_ratio_szamitas(
            napi_hozamok,
            kockazatmentes_hozam
        )
    )

    var_95_szazalek = (
        historikus_var_95(
            napi_hozamok
        )
    )

    beta = beta_szamitas(
        benchmark_adatok
    )

    if (
        var_95_szazalek
        is not None
    ):

        var_95_huf = (
            portfolio_ertek
            * abs(
                var_95_szazalek
            )
            / 100
        )

    else:

        var_95_huf = None

    return {
        "Volatilitás %":
            volatilitas,

        "Max Drawdown %":
            max_drawdown,

        "Sharpe Ratio":
            sharpe,

        "Sortino Ratio":
            sortino,

        "Beta":
            beta,

        "VaR 95% %":
            var_95_szazalek,

        "VaR 95% HUF":
            var_95_huf
    }