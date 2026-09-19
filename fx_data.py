import pandas as pd
import yfinance as yf


# ===================================================
# TÁMOGATOTT DEVIZÁK
# ===================================================

FX_TICKEREK = {
    "USD": "USDHUF=X",
    "EUR": "EURHUF=X",
    "GBP": "GBPHUF=X",
    "CHF": "CHFHUF=X"
}


# ===================================================
# SEGÉDFÜGGVÉNY
# ===================================================

def _deviza_tisztitas(
    deviza
):

    deviza = str(
        deviza
    ).strip().upper()


    if deviza == "HUF":

        return deviza


    if deviza not in FX_TICKEREK:

        raise ValueError(
            f"Nem támogatott deviza: {deviza}"
        )


    return deviza


# ===================================================
# AKTUÁLIS DEVIZAÁRFOLYAM
# ===================================================

def aktualis_huf_arfolyam(
    deviza
):

    deviza = _deviza_tisztitas(
        deviza
    )


    if deviza == "HUF":

        return 1.0


    ticker = FX_TICKEREK[
        deviza
    ]


    try:

        adat = (
            yf.Ticker(
                ticker
            )
            .history(
                period="5d",
                auto_adjust=False
            )
        )


        if adat.empty:

            raise ValueError(
                f"Nincs aktuális árfolyamadat: {ticker}"
            )


        adat = (
            adat
            .dropna(
                subset=[
                    "Close"
                ]
            )
        )


        if adat.empty:

            raise ValueError(
                f"Nincs használható aktuális "
                f"árfolyamadat: {ticker}"
            )


        return float(
            adat[
                "Close"
            ].iloc[-1]
        )


    except Exception as e:

        raise ValueError(
            f"{deviza}/HUF aktuális árfolyam "
            f"lekérése sikertelen: {e}"
        )


# ===================================================
# TÖRTÉNELMI DEVIZAÁRFOLYAM
# ===================================================

def historikus_huf_arfolyam(
    deviza,
    datum
):

    deviza = _deviza_tisztitas(
        deviza
    )


    if deviza == "HUF":

        return 1.0


    datum = pd.Timestamp(
        datum
    ).normalize()


    ticker = FX_TICKEREK[
        deviza
    ]


    # ---------------------------------------------------
    # Nem minden tranzakciós nap kereskedési nap.
    # Ezért néhány nappal korábbról is kérünk adatot.
    # ---------------------------------------------------

    start = (
        datum
        - pd.Timedelta(
            days=7
        )
    )


    end = (
        datum
        + pd.Timedelta(
            days=1
        )
    )


    try:

        adat = (
            yf.download(
                ticker,
                start=start.strftime(
                    "%Y-%m-%d"
                ),
                end=end.strftime(
                    "%Y-%m-%d"
                ),
                progress=False,
                auto_adjust=False
            )
        )


        if adat.empty:

            raise ValueError(
                f"Nincs historikus árfolyamadat "
                f"{datum.date()} dátumhoz."
            )


        close = adat[
            "Close"
        ].dropna()


        # yfinance bizonyos verziókban
        # egy ticker esetén is DataFrame-et adhat.
        if isinstance(
            close,
            pd.DataFrame
        ):

            if close.empty:

                raise ValueError(
                    "A Close oszlop üres."
                )


            close = close.iloc[
                :,
                0
            ]


        close.index = (
            pd.to_datetime(
                close.index
            )
            .tz_localize(
                None
            )
            .normalize()
        )


        # ---------------------------------------------------
        # Csak a tranzakció napján vagy AZELŐTTI
        # árfolyam használható.
        # ---------------------------------------------------

        ervenyes = close[
            close.index
            <= datum
        ]


        if ervenyes.empty:

            raise ValueError(
                f"Nem található {deviza}/HUF "
                f"árfolyam {datum.date()} napjára "
                f"vagy az azt megelőző napokra."
            )


        return float(
            ervenyes.iloc[
                -1
            ]
        )


    except Exception as e:

        raise ValueError(
            f"{deviza}/HUF historikus árfolyam "
            f"lekérése sikertelen "
            f"({datum.date()}): {e}"
        )