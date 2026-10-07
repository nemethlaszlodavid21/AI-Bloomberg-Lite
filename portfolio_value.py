import streamlit as st
import pandas as pd

from market_data import arak_lekerese
from fx_data import aktualis_huf_arfolyam


# ===================================================
# DEVIZAÁRFOLYAM LEKÉRÉSE
# ===================================================

@st.cache_data(ttl=300, show_spinner=False)
def deviza_huf_arfolyam(
    deviza
):

    """
    Aktuális HUF devizaárfolyam lekérése.

    A tényleges adatlekérést az fx_data.py végzi.

    Elsődleges forrás:
    - Yahoo Finance

    Fallback:
    - Frankfurter / MNB

    Így a Streamlit Cloud Yahoo rate limitje
    esetén sem áll le automatikusan a
    portfólióérték számítása.
    """

    return float(
        aktualis_huf_arfolyam(
            deviza
        )
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


        # -----------------------------------------------
        # HA NINCS PIACI ÁR
        # -----------------------------------------------

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