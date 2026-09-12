import pandas as pd
import yfinance as yf

from functools import lru_cache


SECTOR_NEVEK = {

    "technology":
        "Technology",

    "financial_services":
        "Financials",

    "financials":
        "Financials",

    "healthcare":
        "Healthcare",

    "consumer_cyclical":
        "Consumer Cyclical",

    "consumer_defensive":
        "Consumer Defensive",

    "communication_services":
        "Communication Services",

    "industrials":
        "Industrials",

    "energy":
        "Energy",

    "basic_materials":
        "Materials",

    "realestate":
        "Real Estate",

    "real_estate":
        "Real Estate",

    "utilities":
        "Utilities"
}


def _szektor_nev(sector):

    sector = str(
        sector
    ).strip()

    kulcs = (
        sector
        .lower()
        .replace(" ", "_")
    )


    if kulcs in SECTOR_NEVEK:

        return SECTOR_NEVEK[
            kulcs
        ]


    return (
        sector
        .replace("_", " ")
        .title()
    )


def _crypto_e(
    ticker,
    eszkoz
):

    szoveg = (
        f"{ticker} {eszkoz}"
        .upper()
    )

    crypto_szavak = [
        "BTC",
        "BITCOIN",
        "ETH",
        "ETHEREUM"
    ]


    return any(
        szo in szoveg
        for szo in crypto_szavak
    )


@lru_cache(
    maxsize=100
)
def szektorok_lekerese(
    ticker,
    eszkoz=""
):

    # --------------------------------------------
    # CRYPTO
    # --------------------------------------------

    if _crypto_e(
        ticker,
        eszkoz
    ):

        return {
            "Crypto": 1.0
        }


    stock = yf.Ticker(
        ticker
    )


    # --------------------------------------------
    # ETF / FUND LOOK-THROUGH
    # --------------------------------------------

    try:

        fund_data = (
            stock.funds_data
        )

        sector_weightings = (
            fund_data
            .sector_weightings
        )


        if sector_weightings:

            tisztitott = {}


            for sector, weight in (
                sector_weightings.items()
            ):

                if weight is None:
                    continue


                weight = float(
                    weight
                )


                if weight <= 0:
                    continue


                tisztitott[
                    _szektor_nev(
                        sector
                    )
                ] = weight


            if tisztitott:

                osszeg = sum(
                    tisztitott.values()
                )


                # Yahoo normál esetben
                # 0-1 formátumban adja.
                # Ez védi a kódot akkor is,
                # ha százalékos adat érkezne.

                if osszeg > 2:

                    tisztitott = {
                        sector:
                            weight / 100

                        for sector, weight
                        in tisztitott.items()
                    }


                osszeg = sum(
                    tisztitott.values()
                )


                if osszeg > 0:

                    return {
                        sector:
                            weight / osszeg

                        for sector, weight
                        in tisztitott.items()
                    }


    except Exception:

        pass


    # --------------------------------------------
    # EGYEDI RÉSZVÉNY
    # --------------------------------------------

    try:

        info = stock.info

        sector = info.get(
            "sector"
        )


        if sector:

            return {
                _szektor_nev(
                    sector
                ): 1.0
            }


    except Exception:

        pass


    # --------------------------------------------
    # NINCS ADAT
    # --------------------------------------------

    return {
        "Nem besorolt": 1.0
    }


def portfolio_lookthrough(
    portfolio
):

    kitettség = {}


    for _, sor in portfolio.iterrows():

        ticker = str(
            sor["Ticker"]
        )

        eszkoz = str(
            sor["Eszköz"]
        )

        ertek_huf = float(
            sor["HUF érték"]
        )


        sectorok = szektorok_lekerese(
            ticker,
            eszkoz
        )


        for sector, sector_weight in (
            sectorok.items()
        ):

            sector_ertek = (
                ertek_huf
                * sector_weight
            )


            kitettség[
                sector
            ] = (
                kitettség.get(
                    sector,
                    0
                )
                + sector_ertek
            )


    dataframe = pd.DataFrame(
        [
            {
                "Sector": sector,
                "HUF érték": value
            }

            for sector, value
            in kitettség.items()
        ]
    )


    if dataframe.empty:

        return dataframe


    total = dataframe[
        "HUF érték"
    ].sum()


    if total > 0:

        dataframe[
            "Súly %"
        ] = (
            dataframe["HUF érték"]
            / total
            * 100
        )

    else:

        dataframe[
            "Súly %"
        ] = 0


    dataframe = dataframe.sort_values(
        "Súly %",
        ascending=False
    )


    return dataframe.reset_index(
        drop=True
    )