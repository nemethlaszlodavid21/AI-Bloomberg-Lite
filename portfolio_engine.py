import pandas as pd

from fx_data import (
    aktualis_huf_arfolyam,
    historikus_huf_arfolyam
)


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
        "Bekerülési érték HUF",
        "Realizált P/L",
        "Realizált P/L HUF"
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
    # FX CACHE
    # ===================================================

    fx_cache = {}


    def tranzakcios_fx(
        deviza,
        datum
    ):

        kulcs = (
            str(deviza).upper(),
            str(datum)
        )


        if kulcs not in fx_cache:

            fx_cache[
                kulcs
            ] = historikus_huf_arfolyam(
                deviza,
                datum
            )


        return fx_cache[
            kulcs
        ]


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


        trade_date = sor[
            "trade_date"
        ]


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
        # TRANZAKCIÓ NAPI FX
        # -----------------------------------------------

        fx = tranzakcios_fx(
            deviza,
            trade_date
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

                "Bekerülési érték HUF":
                    0.0,

                "Realizált P/L":
                    0.0,

                "Realizált P/L HUF":
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


            teljes_uj_koltseg_huf = (
                teljes_uj_koltseg
                * fx
            )


            uj_bekerules = (
                pozicio[
                    "Bekerülési érték"
                ]
                + teljes_uj_koltseg
            )


            uj_bekerules_huf = (
                pozicio[
                    "Bekerülési érték HUF"
                ]
                + teljes_uj_koltseg_huf
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


            pozicio[
                "Bekerülési érték HUF"
            ] = uj_bekerules_huf


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


            if jelenlegi_darab <= 0:

                raise ValueError(
                    f"{ticker}: nincs eladható pozíció."
                )


            # -----------------------------------------------
            # ÁTLAGOS BEKERÜLÉSI ÉRTÉK / DB
            # -----------------------------------------------

            atlagar = (
                pozicio[
                    "Bekerülési érték"
                ]
                / jelenlegi_darab
            )


            atlagos_huf_bekerules_db = (
                pozicio[
                    "Bekerülési érték HUF"
                ]
                / jelenlegi_darab
            )


            # -----------------------------------------------
            # ELADOTT RÉSZ COST BASIS
            # -----------------------------------------------

            eladott_bekerules = (
                atlagar
                * quantity
            )


            eladott_bekerules_huf = (
                atlagos_huf_bekerules_db
                * quantity
            )


            # -----------------------------------------------
            # ELADÁSI BEVÉTEL
            # -----------------------------------------------

            brutto_bevetel = (
                quantity
                * price
            )


            netto_bevetel = (
                brutto_bevetel
                - fee
            )


            netto_bevetel_huf = (
                netto_bevetel
                * fx
            )


            # -----------------------------------------------
            # REALIZÁLT P/L
            # -----------------------------------------------

            realizalt_profit = (
                netto_bevetel
                - eladott_bekerules
            )


            realizalt_profit_huf = (
                netto_bevetel_huf
                - eladott_bekerules_huf
            )


            pozicio[
                "Realizált P/L"
            ] += realizalt_profit


            pozicio[
                "Realizált P/L HUF"
            ] += realizalt_profit_huf


            # -----------------------------------------------
            # MARADÓ POZÍCIÓ
            # -----------------------------------------------

            pozicio[
                "Darab"
            ] -= quantity


            pozicio[
                "Bekerülési érték"
            ] -= eladott_bekerules


            pozicio[
                "Bekerülési érték HUF"
            ] -= eladott_bekerules_huf


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
                    "Bekerülési érték HUF"
                ] = 0.0


                pozicio[
                    "Átlagár"
                ] = 0.0


            else:

                pozicio[
                    "Átlagár"
                ] = (
                    pozicio[
                        "Bekerülési érték"
                    ]
                    / pozicio[
                        "Darab"
                    ]
                )


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
        "Bekerülési érték HUF",
        "Aktuális érték",
        "Aktuális érték HUF",
        "Profit",
        "Profit %",
        "Hozam %",
        "Nem realizált P/L HUF",
        "Hozam HUF %",
        "Realizált P/L",
        "Realizált P/L HUF"
    ]


    if (
        poziciok is None
        or poziciok.empty
    ):

        return pd.DataFrame(
            columns=oszlopok
        )


    # ===================================================
    # AKTUÁLIS FX CACHE
    # ===================================================

    fx_cache = {}


    def aktualis_fx(
        deviza
    ):

        deviza = str(
            deviza
        ).strip().upper()


        if deviza not in fx_cache:

            fx_cache[
                deviza
            ] = aktualis_huf_arfolyam(
                deviza
            )


        return fx_cache[
            deviza
        ]


    sorok = []


    for _, sor in poziciok.iterrows():

        ticker = sor[
            "Ticker"
        ]


        deviza = str(
            sor[
                "Deviza"
            ]
        ).strip().upper()


        price = aktualis_arok.get(
            ticker
        )


        bekerules = float(
            sor[
                "Bekerülési érték"
            ]
        )


        bekerules_huf = float(
            sor[
                "Bekerülési érték HUF"
            ]
        )


        darab = float(
            sor[
                "Darab"
            ]
        )


        realizalt_pl = float(
            sor[
                "Realizált P/L"
            ]
        )


        realizalt_pl_huf = float(
            sor[
                "Realizált P/L HUF"
            ]
        )


        # -----------------------------------------------
        # NINCS AKTUÁLIS ÁR
        # -----------------------------------------------

        if price is None:

            aktualis_ertek = None

            aktualis_ertek_huf = None

            profit = None

            profit_percent = None

            profit_huf = None

            profit_huf_percent = None


        # -----------------------------------------------
        # VAN AKTUÁLIS ÁR
        # -----------------------------------------------

        else:

            price = float(
                price
            )


            fx = aktualis_fx(
                deviza
            )


            aktualis_ertek = (
                darab
                * price
            )


            aktualis_ertek_huf = (
                aktualis_ertek
                * fx
            )


            # -------------------------------------------
            # NATÍV DEVIZÁS P/L
            # -------------------------------------------

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


            # -------------------------------------------
            # HUF P/L
            # -------------------------------------------

            profit_huf = (
                aktualis_ertek_huf
                - bekerules_huf
            )


            if bekerules_huf != 0:

                profit_huf_percent = (
                    profit_huf
                    / bekerules_huf
                    * 100
                )

            else:

                profit_huf_percent = None


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
                    deviza,

                "Átlagár":
                    float(
                        sor[
                            "Átlagár"
                        ]
                    ),

                "Bekerülési érték":
                    bekerules,

                "Bekerülési érték HUF":
                    bekerules_huf,

                "Aktuális érték":
                    aktualis_ertek,

                "Aktuális érték HUF":
                    aktualis_ertek_huf,

                "Profit":
                    profit,

                "Profit %":
                    profit_percent,

                # ---------------------------------------
                # VISSZAFELÉ KOMPATIBILITÁS
                # ai_analyst.py ezt várja.
                # ---------------------------------------

                "Hozam %":
                    profit_percent,

                "Nem realizált P/L HUF":
                    profit_huf,

                "Hozam HUF %":
                    profit_huf_percent,

                "Realizált P/L":
                    realizalt_pl,

                "Realizált P/L HUF":
                    realizalt_pl_huf
            }
        )


    return pd.DataFrame(
        sorok,
        columns=oszlopok
    )