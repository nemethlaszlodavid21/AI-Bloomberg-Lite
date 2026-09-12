import pandas as pd


# ===================================================
# POZÍCIÓK KISZÁMÍTÁSA
# ===================================================

def poziciok_szamitas_db(
    tranzakciok
):

    oszlopok = [
        "Eszköz",
        "Ticker",
        "Darab",
        "Deviza",
        "Átlagár",
        "Bekerülési érték",
        "Realizált P/L"
    ]


    if (
        tranzakciok is None
        or tranzakciok.empty
    ):

        return pd.DataFrame(
            columns=oszlopok
        )


    tx = (
        tranzakciok
        .copy()
        .sort_values(
            [
                "trade_date",
                "id"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    poziciok = {}


    # ===================================================
    # TRANZAKCIÓK FELDOLGOZÁSA
    # ===================================================

    for _, sor in tx.iterrows():

        ticker = str(
            sor["ticker"]
        ).strip().upper()


        eszkoz = str(
            sor["asset_name"]
        ).strip()


        side = str(
            sor["side"]
        ).strip().upper()


        deviza = str(
            sor["currency"]
        ).strip().upper()


        quantity = float(
            sor["quantity"]
        )


        price = float(
            sor["price"]
        )


        fee = float(
            sor["fee"]
        )


        # -----------------------------------------------
        # ÚJ TICKER
        # -----------------------------------------------

        if ticker not in poziciok:

            poziciok[
                ticker
            ] = {

                "Eszköz":
                    eszkoz,

                "Ticker":
                    ticker,

                "Darab":
                    0.0,

                "Deviza":
                    deviza,

                "Átlagár":
                    0.0,

                "Bekerülési érték":
                    0.0,

                "Realizált P/L":
                    0.0
            }


        pozicio = poziciok[
            ticker
        ]


        # -----------------------------------------------
        # DEVIZA ELLENŐRZÉS
        # -----------------------------------------------

        if (
            pozicio["Deviza"]
            != deviza
        ):

            raise ValueError(
                f"{ticker}: ugyanahhoz a tickerhez "
                f"több deviza szerepel "
                f"({pozicio['Deviza']} és {deviza})."
            )


        pozicio[
            "Eszköz"
        ] = eszkoz


        # ===================================================
        # BUY
        # ===================================================

        if side == "BUY":

            vetel_erteke = (
                quantity
                * price
            )


            teljes_uj_koltseg = (
                vetel_erteke
                + fee
            )


            uj_bekerules = (
                pozicio[
                    "Bekerülési érték"
                ]
                + teljes_uj_koltseg
            )


            uj_darab = (
                pozicio[
                    "Darab"
                ]
                + quantity
            )


            pozicio[
                "Darab"
            ] = uj_darab


            pozicio[
                "Bekerülési érték"
            ] = uj_bekerules


            if uj_darab > 0:

                pozicio[
                    "Átlagár"
                ] = (
                    uj_bekerules
                    / uj_darab
                )


        # ===================================================
        # SELL
        # ===================================================

        elif side == "SELL":

            jelenlegi_darab = (
                pozicio[
                    "Darab"
                ]
            )


            if (
                quantity
                > jelenlegi_darab
                + 1e-10
            ):

                raise ValueError(
                    f"{ticker}: az eladás "
                    f"({quantity:g} db) nagyobb, "
                    f"mint a rendelkezésre álló "
                    f"pozíció "
                    f"({jelenlegi_darab:g} db)."
                )


            atlagar = (
                pozicio[
                    "Átlagár"
                ]
            )


            eladott_bekerules = (
                atlagar
                * quantity
            )


            brutto_bevetel = (
                quantity
                * price
            )


            netto_bevetel = (
                brutto_bevetel
                - fee
            )


            realizalt_profit = (
                netto_bevetel
                - eladott_bekerules
            )


            pozicio[
                "Realizált P/L"
            ] += realizalt_profit


            pozicio[
                "Darab"
            ] -= quantity


            pozicio[
                "Bekerülési érték"
            ] -= eladott_bekerules


            # -----------------------------------------------
            # TELJESEN LEZÁRT POZÍCIÓ
            # -----------------------------------------------

            if abs(
                pozicio[
                    "Darab"
                ]
            ) < 1e-10:

                pozicio[
                    "Darab"
                ] = 0.0


                pozicio[
                    "Bekerülési érték"
                ] = 0.0


                pozicio[
                    "Átlagár"
                ] = 0.0


        else:

            raise ValueError(
                f"Ismeretlen tranzakciótípus: "
                f"{side}"
            )


    # ===================================================
    # CSAK AKTÍV POZÍCIÓK
    # ===================================================

    aktiv = [

        adat

        for adat
        in poziciok.values()

        if adat[
            "Darab"
        ] > 1e-10
    ]


    return pd.DataFrame(
        aktiv,
        columns=oszlopok
    )


# ===================================================
# PORTFÓLIÓ DATAFRAME
# ===================================================

def portfolio_adatframe_db(
    tranzakciok
):

    poziciok = (
        poziciok_szamitas_db(
            tranzakciok
        )
    )


    if poziciok.empty:

        return pd.DataFrame(
            columns=[
                "Eszköz",
                "Ticker",
                "Darab",
                "Deviza"
            ]
        )


    return poziciok[
        [
            "Eszköz",
            "Ticker",
            "Darab",
            "Deviza"
        ]
    ].copy()


# ===================================================
# PERFORMANCE
# ===================================================

def performance_szamitas_db(
    poziciok,
    aktualis_arok
):

    oszlopok = [
        "Eszköz",
        "Ticker",
        "Darab",
        "Deviza",
        "Átlagár",
        "Bekerülési érték",
        "Aktuális érték",
        "Profit",
        "Profit %",
        "Hozam %",
        "Realizált P/L"
    ]


    if (
        poziciok is None
        or poziciok.empty
    ):

        return pd.DataFrame(
            columns=oszlopok
        )


    sorok = []


    for _, sor in poziciok.iterrows():

        ticker = sor[
            "Ticker"
        ]


        price = aktualis_arok.get(
            ticker
        )


        bekerules = float(
            sor[
                "Bekerülési érték"
            ]
        )


        darab = float(
            sor[
                "Darab"
            ]
        )


        # -----------------------------------------------
        # NINCS AKTUÁLIS ÁR
        # -----------------------------------------------

        if price is None:

            aktualis_ertek = None

            profit = None

            profit_percent = None


        # -----------------------------------------------
        # VAN AKTUÁLIS ÁR
        # -----------------------------------------------

        else:

            aktualis_ertek = (
                darab
                * float(
                    price
                )
            )


            profit = (
                aktualis_ertek
                - bekerules
            )


            if bekerules != 0:

                profit_percent = (
                    profit
                    / bekerules
                    * 100
                )

            else:

                profit_percent = None


        sorok.append(
            {

                "Eszköz":
                    sor[
                        "Eszköz"
                    ],

                "Ticker":
                    ticker,

                "Darab":
                    darab,

                "Deviza":
                    sor[
                        "Deviza"
                    ],

                "Átlagár":
                    float(
                        sor[
                            "Átlagár"
                        ]
                    ),

                "Bekerülési érték":
                    bekerules,

                "Aktuális érték":
                    aktualis_ertek,

                "Profit":
                    profit,

                "Profit %":
                    profit_percent,

                # FONTOS:
                # ai_analyst.py ezt az oszlopot várja.
                "Hozam %":
                    profit_percent,

                "Realizált P/L":
                    float(
                        sor[
                            "Realizált P/L"
                        ]
                    )
            }
        )


    return pd.DataFrame(
        sorok,
        columns=oszlopok
    )