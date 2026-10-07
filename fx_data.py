import streamlit as st
import pandas as pd
import yfinance as yf


# ===================================================
# TÁMOGATOTT DEVIZÁK
# ===================================================

FX_TICKEREK = {
    "USD": "USDHUF=X",
    "EUR": "EURHUF=X",
    "GBP": "GBPHUF=X",
    "CHF": "CHFHUF=X",
}


# ===================================================
# SEGÉDFÜGGVÉNY
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


def _close_sorozat(adat):

    if adat is None or adat.empty:
        return pd.Series(dtype=float)

    if "Close" not in adat.columns:
        return pd.Series(dtype=float)

    close = adat["Close"]

    # yfinance bizonyos verziókban
    # DataFrame-et ad vissza egy ticker esetén is
    if isinstance(close, pd.DataFrame):

        if close.empty:
            return pd.Series(dtype=float)

        close = close.iloc[:, 0]

    close = close.dropna()

    if close.empty:
        return pd.Series(dtype=float)

    close.index = (
        pd.to_datetime(close.index)
        .tz_localize(None)
        .normalize()
    )

    return close


# ===================================================
# AKTUÁLIS DEVIZAÁRFOLYAM
# ===================================================

@st.cache_data(ttl=300, show_spinner=False)
def aktualis_huf_arfolyam(deviza):

    deviza = _deviza_tisztitas(deviza)

    if deviza == "HUF":
        return 1.0

    ticker = FX_TICKEREK[deviza]

    try:

        adat = (
            yf.Ticker(ticker)
            .history(
                period="5d",
                auto_adjust=False
            )
        )

        close = _close_sorozat(adat)

        if close.empty:
            raise ValueError(
                f"Nincs aktuális árfolyamadat: {ticker}"
            )

        return float(close.iloc[-1])

    except Exception as e:

        raise ValueError(
            f"{deviza}/HUF aktuális árfolyam "
            f"lekérése sikertelen: {e}"
        )


# ===================================================
# TÖRTÉNELMI DEVIZAÁRFOLYAM
# ===================================================

@st.cache_data(ttl=86400, show_spinner=False)
def historikus_huf_arfolyam(deviza, datum):

    deviza = _deviza_tisztitas(deviza)

    if deviza == "HUF":
        return 1.0

    datum = pd.Timestamp(datum).normalize()

    ticker = FX_TICKEREK[deviza]

    # ---------------------------------------------------
    # Visszafelé keresési ablak
    #
    # Hétvége, ünnepnap vagy hiányzó Yahoo-adat esetén
    # az utolsó elérhető korábbi árfolyamot használjuk.
    # ---------------------------------------------------

    start = datum - pd.Timedelta(days=10)
    end = datum + pd.Timedelta(days=1)

    hibak = []

    # ===================================================
    # 1. PRÓBÁLKOZÁS – yf.download()
    # ===================================================

    try:

        adat = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=False,
            threads=False,
        )

        close = _close_sorozat(adat)

        if not close.empty:

            ervenyes = close[
                close.index <= datum
            ]

            if not ervenyes.empty:
                return float(
                    ervenyes.iloc[-1]
                )

        hibak.append(
            "yf.download nem adott használható adatot"
        )

    except Exception as e:

        hibak.append(
            f"yf.download: {e}"
        )

    # ===================================================
    # 2. PRÓBÁLKOZÁS – Ticker.history()
    # ===================================================

    try:

        adat = (
            yf.Ticker(ticker)
            .history(
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
                auto_adjust=False,
            )
        )

        close = _close_sorozat(adat)

        if not close.empty:

            ervenyes = close[
                close.index <= datum
            ]

            if not ervenyes.empty:
                return float(
                    ervenyes.iloc[-1]
                )

        hibak.append(
            "Ticker.history nem adott használható adatot"
        )

    except Exception as e:

        hibak.append(
            f"Ticker.history: {e}"
        )

    # ===================================================
    # HA EGYIK FORRÁS SEM SIKERÜLT
    # ===================================================

    raise ValueError(
        f"{deviza}/HUF historikus árfolyam "
        f"lekérése sikertelen "
        f"({datum.date()}). "
        f"Nincs használható árfolyam a "
        f"{start.date()}–{datum.date()} időszakban. "
        f"Részletek: {' | '.join(hibak)}"
    )