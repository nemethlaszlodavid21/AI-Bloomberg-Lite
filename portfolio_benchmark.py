import pandas as pd
import yfinance as yf
import streamlit as st


IDOTAVOK = {
    "1M": 31,
    "3M": 93,
    "6M": 186,
    "1Y": 366
}


@st.cache_data(ttl=900)
def _market_history(
    ticker,
    start_date,
    end_date
):

    try:

        adat = yf.Ticker(
            ticker
        ).history(
            start=start_date,
            end=end_date
        )

        if adat.empty:
            return pd.Series(dtype=float)

        sorozat = adat[
            "Close"
        ].copy()

        sorozat.index = pd.to_datetime(
            sorozat.index
        )

        if sorozat.index.tz is not None:

            sorozat.index = (
                sorozat.index
                .tz_localize(None)
            )

        return sorozat

    except Exception:

        return pd.Series(
            dtype=float
        )


def _normalizalas(
    sorozat
):

    sorozat = (
        sorozat
        .dropna()
        .astype(float)
    )

    if sorozat.empty:
        return sorozat

    elso_ertek = (
        sorozat.iloc[0]
    )

    if elso_ertek == 0:
        return sorozat

    return (
        sorozat
        / elso_ertek
        * 100
    )


def _benchmark_huf(
    index_ticker,
    usd_huf,
    portfolio_index,
    start_date,
    end_date
):

    index_ar = _market_history(
        index_ticker,
        start_date,
        end_date
    )

    if index_ar.empty:
        return pd.Series(dtype=float)

    kozos_index = (
        index_ar.index
        .union(usd_huf.index)
        .sort_values()
    )

    index_ar = (
        index_ar
        .reindex(kozos_index)
        .ffill()
    )

    fx = (
        usd_huf
        .reindex(kozos_index)
        .ffill()
    )

    index_huf = (
        index_ar
        * fx
    )

    index_huf = (
        index_huf
        .reindex(
            portfolio_index
        )
        .ffill()
        .bfill()
    )

    return _normalizalas(
        index_huf
    )


def benchmark_osszehasonlitas(
    tortenet,
    idotav="1Y"
):

    if (
        tortenet is None
        or tortenet.empty
        or "Portfolio" not in tortenet.columns
    ):

        return pd.DataFrame()


    adat = tortenet.copy()

    adat.index = pd.to_datetime(
        adat.index
    )


    if adat.index.tz is not None:

        adat.index = (
            adat.index
            .tz_localize(None)
        )


    adat = adat.sort_index()


    napok = IDOTAVOK.get(
        idotav,
        366
    )


    utolso_datum = (
        adat.index.max()
    )


    kezdo_datum = (
        utolso_datum
        - pd.Timedelta(
            days=napok
        )
    )


    adat = adat.loc[
        adat.index >= kezdo_datum
    ]


    if adat.empty:
        return pd.DataFrame()


    portfolio_index = (
        adat.index
    )


    portfolio_normalizalt = (
        _normalizalas(
            adat["Portfolio"]
        )
    )


    start_date = (
        portfolio_index.min()
        - pd.Timedelta(
            days=7
        )
    )


    end_date = (
        portfolio_index.max()
        + pd.Timedelta(
            days=2
        )
    )


    usd_huf = _market_history(
        "USDHUF=X",
        start_date,
        end_date
    )


    sp500 = _benchmark_huf(
        "^GSPC",
        usd_huf,
        portfolio_index,
        start_date,
        end_date
    )


    nasdaq = _benchmark_huf(
        "^NDX",
        usd_huf,
        portfolio_index,
        start_date,
        end_date
    )


    eredmeny = pd.DataFrame(
        index=portfolio_index
    )


    eredmeny[
        "Portfolio"
    ] = portfolio_normalizalt


    if not sp500.empty:

        eredmeny[
            "S&P 500"
        ] = sp500


    if not nasdaq.empty:

        eredmeny[
            "Nasdaq 100"
        ] = nasdaq


    eredmeny = (
        eredmeny
        .ffill()
        .dropna(
            how="all"
        )
    )


    return eredmeny


def benchmark_hozamok(
    benchmark_adatok
):

    eredmeny = {}


    if (
        benchmark_adatok is None
        or benchmark_adatok.empty
    ):

        return eredmeny


    for oszlop in (
        benchmark_adatok.columns
    ):

        sorozat = (
            benchmark_adatok[
                oszlop
            ]
            .dropna()
        )

        if len(sorozat) < 2:
            continue


        hozam = (
            (
                sorozat.iloc[-1]
                / sorozat.iloc[0]
            )
            - 1
        ) * 100


        eredmeny[
            oszlop
        ] = float(
            hozam
        )


    return eredmeny