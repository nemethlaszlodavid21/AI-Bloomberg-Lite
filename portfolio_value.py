import pandas as pd
import yfinance as yf

from market_data import arak_lekerese


# ===================================================
# DEVIZAÁRFOLYAM LEKÉRÉSE
# ===================================================

def deviza_huf_arfolyam(
    deviza
):

    deviza = str(
        deviza
    ).strip().upper()


    # -----------------------------------------------
    # HUF
    # -----------------------------------------------

    if deviza == "HUF":

        return 1.0


    # -----------------------------------------------
    # YAHOO FX TICKEREK
    # -----------------------------------------------

    fx_tickerek = {

        "USD":
            "USDHUF=X",

        "EUR":
            "EURHUF=X",

        "GBP":
            "GBPHUF=X",

        "CHF":
            "CHFHUF=X"
    }


    if deviza not in fx_tickerek:

        raise ValueError(
            f"Nem támogatott deviza: {deviza}"
        )


    fx_ticker = (
        fx_tickerek[
            deviza
        ]
    )


    try:

        adat = (
            yf.Ticker(
                fx_ticker
            )
            .history(
                period="5d"
            )
        )


        if adat.empty:

            raise ValueError(
                f"Nincs árfolyamadat: {fx_ticker}"
            )


        adat = (
            adat.dropna(
                subset=[
                    "Close"
                ]
            )
        )


        if adat.empty:

            raise ValueError(
                f"Nincs használható árfolyamadat: {fx_ticker}"
            )


        arfolyam = float(
            adat[
                "Close"
            ].iloc[-1]
        )


        return arfolyam


    except Exception as e:

        raise ValueError(
            f"{deviza}/HUF árfolyam lekérése sikertelen: {e}"
        )


# ===================================================
# PORTFÓLIÓ ÉRTÉK SZÁMÍTÁS
# ===================================================

def portfolio_ertek_szamitas(
    portfolio
):

    # -----------------------------------------------
    # ÜRES PORTFÓLIÓ
    # -----------------------------------------------

    if (
        portfolio is None
        or portfolio.empty
    ):

        ures = (
            portfolio.copy()
            if portfolio is not None
            else pd.DataFrame()
        )


        ures[
            "Ár"
        ] = pd.Series(
            dtype=float
        )


        ures[
            "HUF árfolyam"
        ] = pd.Series(
            dtype=float
        )


        ures[
            "HUF érték"
        ] = pd.Series(
            dtype=float
        )


        return ures


    # -----------------------------------------------
    # MÁSOLAT
    # -----------------------------------------------

    eredmeny = (
        portfolio.copy()
    )


    # -----------------------------------------------
    # AKTUÁLIS PIACI ÁRAK
    # -----------------------------------------------

    tickerek = (
        eredmeny[
            "Ticker"
        ]
        .astype(str)
        .tolist()
    )


    aktualis_arok = (
        arak_lekerese(
            tickerek
        )
    )


    # -----------------------------------------------
    # DEVIZAÁRFOLYAMOK
    # -----------------------------------------------

    devizak = (
        eredmeny[
            "Deviza"
        ]
        .astype(str)
        .str.upper()
        .unique()
        .tolist()
    )


    fx_arfolyamok = {}


    for deviza in devizak:

        fx_arfolyamok[
            deviza
        ] = (
            deviza_huf_arfolyam(
                deviza
            )
        )


    # -----------------------------------------------
    # SORONKÉNTI SZÁMÍTÁS
    # -----------------------------------------------

    arak = []

    huf_arfolyamok = []

    huf_ertekek = []


    for _, sor in eredmeny.iterrows():

        ticker = str(
            sor[
                "Ticker"
            ]
        ).strip()


        deviza = str(
            sor[
                "Deviza"
            ]
        ).strip().upper()


        darab = float(
            sor[
                "Darab"
            ]
        )


        aktualis_ar = (
            aktualis_arok.get(
                ticker
            )
        )


        if aktualis_ar is None:

            arak.append(
                None
            )

            huf_arfolyamok.append(
                fx_arfolyamok.get(
                    deviza
                )
            )

            huf_ertekek.append(
                0.0
            )

            continue


        aktualis_ar = float(
            aktualis_ar
        )


        fx = float(
            fx_arfolyamok[
                deviza
            ]
        )


        # -----------------------------------------------
        # PIACI ÉRTÉK SAJÁT DEVIZÁBAN
        # -----------------------------------------------

        piaci_ertek_deviza = (
            darab
            * aktualis_ar
        )


        # -----------------------------------------------
        # PIACI ÉRTÉK HUF-BAN
        # -----------------------------------------------

        huf_ertek = (
            piaci_ertek_deviza
            * fx
        )


        arak.append(
            aktualis_ar
        )


        huf_arfolyamok.append(
            fx
        )


        huf_ertekek.append(
            huf_ertek
        )


    # -----------------------------------------------
    # EREDMÉNY
    # -----------------------------------------------

    eredmeny[
        "Ár"
    ] = arak


    eredmeny[
        "HUF árfolyam"
    ] = huf_arfolyamok


    eredmeny[
        "HUF érték"
    ] = huf_ertekek


    return eredmeny