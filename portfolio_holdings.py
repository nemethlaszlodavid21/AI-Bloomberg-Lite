import pandas as pd


def _ertek(
    dataframe,
    ticker,
    eszkoz,
    oszlop
):

    if dataframe is None:
        return None

    if dataframe.empty:
        return None

    talalat = pd.DataFrame()


    if "Ticker" in dataframe.columns:

        talalat = dataframe[
            dataframe["Ticker"].astype(str)
            == str(ticker)
        ]


    if (
        talalat.empty
        and "Eszköz" in dataframe.columns
    ):

        talalat = dataframe[
            dataframe["Eszköz"].astype(str)
            == str(eszkoz)
        ]


    if talalat.empty:
        return None


    if oszlop not in talalat.columns:
        return None


    return talalat.iloc[0][oszlop]


def _napi_valtozas(
    napi_adatok,
    ticker,
    eszkoz
):

    if not napi_adatok:
        return None


    for adat in napi_adatok:

        adat_ticker = str(
            adat.get(
                "Ticker",
                ""
            )
        )

        adat_eszkoz = str(
            adat.get(
                "Eszköz",
                ""
            )
        )


        if (
            adat_ticker == str(ticker)
            or adat_eszkoz == str(eszkoz)
        ):

            return adat.get(
                "Napi változás %",
                None
            )


    return None


def holdings_tabla_keszites(
    portfolio,
    performance,
    aktualis_arok,
    napi_adatok,
    teljes_portfolio_ertek
):

    sorok = []


    for _, sor in portfolio.iterrows():

        ticker = sor["Ticker"]

        eszkoz = sor["Eszköz"]

        darab = sor["Darab"]

        deviza = sor.get(
            "Deviza",
            ""
        )


        price = aktualis_arok.get(
            ticker,
            None
        )


        market_value = _ertek(
            performance,
            ticker,
            eszkoz,
            "Aktuális érték"
        )


        cost_basis = _ertek(
            performance,
            ticker,
            eszkoz,
            "Bekerülési érték"
        )


        profit = _ertek(
            performance,
            ticker,
            eszkoz,
            "Profit"
        )


        if (
            cost_basis is not None
            and cost_basis != 0
            and profit is not None
        ):

            profit_percent = (
                profit
                / cost_basis
                * 100
            )

        else:

            profit_percent = None


        market_value_huf = sor.get(
            "HUF érték",
            0
        )


        if teljes_portfolio_ertek > 0:

            weight = (
                market_value_huf
                / teljes_portfolio_ertek
                * 100
            )

        else:

            weight = 0


        daily_percent = _napi_valtozas(
            napi_adatok,
            ticker,
            eszkoz
        )


        sorok.append(
            {
                "Asset": eszkoz,
                "Ticker": ticker,
                "Quantity": darab,
                "Price": price,
                "Currency": deviza,
                "Market Value": market_value,
                "Weight %": weight,
                "Cost Basis": cost_basis,
                "P/L": profit,
                "P/L %": profit_percent,
                "Daily %": daily_percent
            }
        )


    return pd.DataFrame(
        sorok
    )