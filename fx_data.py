import json
import urllib.request

import pandas as pd
import streamlit as st
import yfinance as yf


# ===================================================
# DEVIZA → YAHOO FINANCE TICKER
# ===================================================

FX_TICKEREK = {
    "USD": "USDHUF=X",
    "EUR": "EURHUF=X",
    "GBP": "GBPHUF=X",
    "CHF": "CHFHUF=X",
}


# ===================================================
# DEVIZA TISZTÍTÁSA
# ===================================================

def _deviza_tisztitas(deviza):

    deviza = str(deviza).strip().upper()

    if deviza == "HUF":
        return deviza

    if deviza not in FX_TICKEREK:
        raise ValueError(
            f"Nem támogatott deviza: {deviza}"
        )

    return deviza


# ===================================================
# CLOSE ADAT KINYERÉSE
# ===================================================

def _close_sorozat(adat):

    if adat is None or adat.empty:
        return pd.Series(dtype=float)

    if "Close" not in adat.columns:
        return pd.Series(dtype=float)

    close = adat["Close"]

    if isinstance(close, pd.DataFrame):

        if close.empty:
            return pd.Series(dtype=float)

        close = close.iloc[:, 0]

    close = close.dropna()

    if close.empty:
        return pd.Series(dtype=float)

    close.index = pd.to_datetime(
        close.index
    )

    try:
        close.index = close.index.tz_localize(None)
    except TypeError:
        pass

    close.index = close.index.normalize()

    return close


# ===================================================
# MNB / FRANKFURTER ÁRFOLYAM
# ===================================================

def _mnb_historikus_arfolyam(
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

    hibak = []

    # ---------------------------------------------------
    # Maximum 10 napot keresünk visszafelé.
    #
    # Ez kezeli:
    # - hétvégét
    # - ünnepnapot
    # - hiányzó napi adatot
    # ---------------------------------------------------

    for nap_vissza in range(0, 11):

        keresett_datum = (
            datum
            - pd.Timedelta(
                days=nap_vissza
            )
        )

        url = (
            "https://api.frankfurter.dev/"
            "v2/providers/mnb/rate/"
            f"{deviza.lower()}/huf"
            "?date="
            f"{keresett_datum.strftime('%Y-%m-%d')}"
        )

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                        "AI-Bloomberg-Lite/1.0",
                    "Accept":
                        "application/json",
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:

                adat = json.loads(
                    response
                    .read()
                    .decode("utf-8")
                )

            rate = adat.get(
                "rate"
            )

            if rate is not None:

                rate = float(
                    rate
                )

                if rate > 0:
                    return rate

        except Exception as e:

            hibak.append(
                f"{keresett_datum.date()}: {e}"
            )

    raise ValueError(
        "Frankfurter/MNB nem adott "
        "használható árfolyamot. "
        + (
            " | ".join(hibak[-3:])
            if hibak
            else ""
        )
    )


# ===================================================
# AKTUÁLIS DEVIZAÁRFOLYAM
# ===================================================

@st.cache_data(
    ttl=300,
    show_spinner=False
)
def aktualis_huf_arfolyam(deviza):

    deviza = _deviza_tisztitas(
        deviza
    )

    if deviza == "HUF":
        return 1.0

    ticker = FX_TICKEREK[
        deviza
    ]

    hibak = []

    # ===================================================
    # 1. YAHOO FINANCE
    # ===================================================

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

        close = _close_sorozat(
            adat
        )

        if not close.empty:

            return float(
                close.iloc[-1]
            )

        hibak.append(
            "Yahoo Finance nem adott "
            "használható adatot"
        )

    except Exception as e:

        hibak.append(
            f"Yahoo Finance: {e}"
        )

    # ===================================================
    # 2. FRANKFURTER / MNB FALLBACK
    # ===================================================

    try:

        mai_datum = (
            pd.Timestamp.now()
            .normalize()
        )

        return float(
            _mnb_historikus_arfolyam(
                deviza,
                mai_datum
            )
        )

    except Exception as e:

        hibak.append(
            f"Frankfurter/MNB: {e}"
        )

    # ===================================================
    # MINDEN FORRÁS SIKERTELEN
    # ===================================================

    raise ValueError(
        f"{deviza}/HUF aktuális árfolyam "
        f"lekérése sikertelen. "
        f"Részletek: {' | '.join(hibak)}"
    )


# ===================================================
# HISTORIKUS DEVIZAÁRFOLYAM
# ===================================================

@st.cache_data(
    ttl=86400,
    show_spinner=False
)
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
    # 10 napos visszafelé keresési ablak
    # ---------------------------------------------------

    start = (
        datum
        - pd.Timedelta(
            days=10
        )
    )

    end = (
        datum
        + pd.Timedelta(
            days=1
        )
    )

    hibak = []

    # ===================================================
    # 1. YAHOO – DOWNLOAD
    # ===================================================

    try:

        adat = yf.download(
            ticker,
            start=start.strftime(
                "%Y-%m-%d"
            ),
            end=end.strftime(
                "%Y-%m-%d"
            ),
            progress=False,
            auto_adjust=False,
            threads=False,
        )

        close = _close_sorozat(
            adat
        )

        if not close.empty:

            ervenyes = close[
                close.index <= datum
            ]

            if not ervenyes.empty:

                return float(
                    ervenyes.iloc[-1]
                )

        hibak.append(
            "yf.download nem adott "
            "használható adatot"
        )

    except Exception as e:

        hibak.append(
            f"yf.download: {e}"
        )

    # ===================================================
    # 2. YAHOO – TICKER.HISTORY
    # ===================================================

    try:

        adat = (
            yf.Ticker(
                ticker
            )
            .history(
                start=start.strftime(
                    "%Y-%m-%d"
                ),
                end=end.strftime(
                    "%Y-%m-%d"
                ),
                auto_adjust=False,
            )
        )

        close = _close_sorozat(
            adat
        )

        if not close.empty:

            ervenyes = close[
                close.index <= datum
            ]

            if not ervenyes.empty:

                return float(
                    ervenyes.iloc[-1]
                )

        hibak.append(
            "Ticker.history nem adott "
            "használható adatot"
        )

    except Exception as e:

        hibak.append(
            f"Ticker.history: {e}"
        )

    # ===================================================
    # 3. MNB / FRANKFURTER FALLBACK
    # ===================================================

    try:

        return float(
            _mnb_historikus_arfolyam(
                deviza,
                datum
            )
        )

    except Exception as e:

        hibak.append(
            f"Frankfurter/MNB: {e}"
        )

    # ===================================================
    # MINDEN FORRÁS SIKERTELEN
    # ===================================================

    raise ValueError(
        f"{deviza}/HUF historikus árfolyam "
        f"lekérése sikertelen "
        f"({datum.date()}). "
        f"Nincs használható árfolyam a "
        f"{start.date()}–{datum.date()} "
        f"időszakban. "
        f"Részletek: {' | '.join(hibak)}"
    )