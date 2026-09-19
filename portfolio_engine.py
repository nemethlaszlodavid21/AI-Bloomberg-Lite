import pandas as pd

from fx_data import (
    aktualis_huf_arfolyam,
    historikus_huf_arfolyam
)

from corporate_actions import (
    ticker_corporate_actions
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

    # ===================================================
    # RENDEZÉS
    # ===================================================

    tx = tranzakciok.copy()

    tx["trade_date"] = pd.to_datetime(
        tx["trade_date"]
    )

    rendezes = [
        "trade_date"
    ]

    if "trade_datetime" in tx.columns:
        rendezes.append(
            "trade_datetime"
        )

    if "id" in tx.columns:
        rendezes.append(
            "id"
        )

    tx = (
        tx
        .sort_values(
            rendezes,
            na_position="last"
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
    # CORPORATE ACTION SEGÉDFÜGGVÉNY
    # ===================================================

    def corporate_actions_alkalmazasa(
        ticker,
        pozicio,
        elozo_datum,
        aktualis_datum
    ):

        actions = ticker_corporate_actions(
            ticker
        )

        if actions.empty:
            return

        elozo_datum = pd.Timestamp(
            elozo_datum
        )

        aktualis_datum = pd.Timestamp(
            aktualis_datum
        )

        relevant_actions = actions[
            (actions["date"] > elozo_datum)
            &
            (actions["date"] <= aktualis_datum)
        ]

        for _, action in (
            relevant_actions.iterrows()
        ):

            action_type = str(
                action["type"]
            ).strip().upper()

            if action_type != "SPLIT":
                continue

            ratio = float(
                action["split_ratio"]
            )

            if ratio <= 0:
                raise ValueError(
                    f"{ticker}: hibás split ratio: "
                    f"{ratio}"
                )

            # -----------------------------------------------
            # SPLIT / REVERSE SPLIT
            # -----------------------------------------------
            #
            # Darabszám változik.
            #
            # A teljes bekerülési érték NEM változik.
            #
            # Emiatt az átlagár automatikusan
            # újraszámolható.
            # -----------------------------------------------

            pozicio[
                "Darab"
            ] *= ratio

            if (
                pozicio["Darab"]
                > 1e-10
            ):

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

                pozicio[
                    "Darab"
                ] = 0.0

                pozicio[
                    "Átlagár"
                ] = 0.0

    # ===================================================
    # UTOLSÓ FELDOLGOZOTT DÁTUM TICKERENKÉNT
    # ===================================================

    utolso_datum = {}

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

        trade_date = pd.Timestamp(
            sor["trade_date"]
        )

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
        # FORRÁS
        # -----------------------------------------------

        source = str(
            sor.get(
                "source",
                "MANUAL"
            )
        ).strip().upper()

        if source in {
            "",
            "NONE",
            "NAN"
        }:

            source = "MANUAL"

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

        # ===================================================
        # CORPORATE ACTION A KÉT TRANZAKCIÓ KÖZÖTT
        # ===================================================

        if ticker in utolso_datum:

            corporate_actions_alkalmazasa(
                ticker=ticker,
                pozicio=pozicio,
                elozo_datum=utolso_datum[ticker],
                aktualis_datum=trade_date
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

            jelenlegi_darab = float(
                pozicio[
                    "Darab"
                ]
            )

            # ===================================================
            # ELADOTT MENNYISÉG FELBONTÁSA
            # ===================================================

            if (
                quantity
                > jelenlegi_darab
                + 1e-10
            ):

                if source in {
                    "IBKR",
                    "EXCEL"
                }:

                    ismert_eladott_darab = max(
                        jelenlegi_darab,
                        0.0
                    )

                    ismeretlen_eladott_darab = (
                        quantity
                        - ismert_eladott_darab
                    )

                else:

                    raise ValueError(
                        f"{ticker}: az eladás "
                        f"({quantity:g} db) nagyobb, "
                        f"mint a rendelkezésre álló "
                        f"pozíció "
                        f"({jelenlegi_darab:g} db)."
                    )

            else:

                ismert_eladott_darab = quantity

                ismeretlen_eladott_darab = 0.0

            # ===================================================
            # ISMERT COST BASISŰ RÉSZ
            # ===================================================

            if (
                ismert_eladott_darab
                > 1e-10
            ):

                if jelenlegi_darab <= 0:

                    raise ValueError(
                        f"{ticker}: nincs eladható "
                        f"ismert pozíció."
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
                    * ismert_eladott_darab
                )

                eladott_bekerules_huf = (
                    atlagos_huf_bekerules_db
                    * ismert_eladott_darab
                )

                # -----------------------------------------------
                # JUTALÉK ARÁNYOS RÉSZE
                # -----------------------------------------------

                if quantity > 0:

                    ismert_fee = (
                        fee
                        * (
                            ismert_eladott_darab
                            / quantity
                        )
                    )

                else:

                    ismert_fee = 0.0

                # -----------------------------------------------
                # ELADÁSI BEVÉTEL
                # -----------------------------------------------

                brutto_bevetel = (
                    ismert_eladott_darab
                    * price
                )

                netto_bevetel = (
                    brutto_bevetel
                    - ismert_fee
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
                ] -= ismert_eladott_darab

                pozicio[
                    "Bekerülési érték"
                ] -= eladott_bekerules

                pozicio[
                    "Bekerülési érték HUF"
                ] -= eladott_bekerules_huf

            # ===================================================
            # ISMERETLEN ELŐZMÉNYŰ RÉSZ
            # ===================================================
            #
            # Importált részleges történetnél:
            #
            # - nem hozunk létre negatív pozíciót
            # - nem találunk ki cost basist
            # - nem számolunk kitalált realizált P/L-t
            # ===================================================

            if (
                ismeretlen_eladott_darab
                > 1e-10
            ):

                pass

            # ===================================================
            # POZÍCIÓ NORMALIZÁLÁSA
            # ===================================================

            if (
                pozicio[
                    "Darab"
                ]
                < 1e-10
            ):

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

        # ===================================================
        # ISMERETLEN TRANZAKCIÓTÍPUS
        # ===================================================

        else:

            raise ValueError(
                f"Ismeretlen tranzakciótípus: "
                f"{side}"
            )

        # -----------------------------------------------
        # UTOLSÓ TRANZAKCIÓ DÁTUMA
        # -----------------------------------------------

        utolso_datum[
            ticker
        ] = trade_date

    # ===================================================
    # UTOLSÓ TRANZAKCIÓ UTÁNI CORPORATE ACTIONÖK
    # ===================================================
    #
    # Ez szükséges például az IMUX esetében:
    #
    # BUY:   2026-02-24
    # SPLIT: 2026-04-27
    #
    # Ha nincs split után újabb tranzakció,
    # akkor itt alkalmazzuk az eseményt.
    # ===================================================

    mai_datum = pd.Timestamp.now()

    for ticker, pozicio in (
        poziciok.items()
    ):

        if ticker not in utolso_datum:
            continue

        corporate_actions_alkalmazasa(
            ticker=ticker,
            pozicio=pozicio,
            elozo_datum=utolso_datum[ticker],
            aktualis_datum=mai_datum
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