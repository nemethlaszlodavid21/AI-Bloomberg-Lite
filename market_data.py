import streamlit as st
import yfinance as yf


# ==================================================
# IBKR → YAHOO FINANCE TICKER MAPPING
# ==================================================
#
# Az IBKR Activity Statement gyakran csak a rövid
# tickert tartalmazza, miközben ugyanaz a ticker
# több tőzsdén / devizában is létezhet.
#
# Itt azt a Yahoo Finance instrumentumot adjuk meg,
# amely megfelel az IBKR-ben tartott instrumentumnak.
# ==================================================

TICKER_MAPPING = {
    "BTCN": "BTCN.AS",
    "ASOL": "ASOL.DE",
    "ZETH": "ZETH.DE",
    "OTP": "OTP.BD",
    "SMH": "SMH.L",
    "CNDX": "CNDX.L",
    "QNTM": "QNTM.L",
    "EQQQ": "EQQQ.SW",
    "JEDI": "JEDI.L",

    # Új mappingek
    "ZPDE": "ZPDE.DE",
    "SMH3": "SMH3.L",
    "QQQ3": "QQQ3.L",
}


# ==================================================
# YAHOO TICKER FELOLDÁSA
# ==================================================

def yahoo_ticker(ticker):

    ticker = str(
        ticker
    ).strip().upper()

    return TICKER_MAPPING.get(
        ticker,
        ticker
    )


# ==================================================
# AKTUÁLIS ÁRFOLYAM
# ==================================================

@st.cache_data(ttl=300, show_spinner=False)
def get_price(ticker):

    eredeti_ticker = str(
        ticker
    ).strip().upper()

    yahoo_symbol = yahoo_ticker(
        eredeti_ticker
    )

    # --------------------------------------------------
    # YAHOO INSTRUMENTUM
    # --------------------------------------------------

    instrument = yf.Ticker(
        yahoo_symbol
    )

    # --------------------------------------------------
    # ÁRFOLYAMADAT
    # --------------------------------------------------

    data = instrument.history(
        period="5d",
        auto_adjust=True
    )

    if data.empty:

        raise Exception(
            f"Nincs árfolyamadat: "
            f"{eredeti_ticker} "
            f"({yahoo_symbol})"
        )

    close = (
        data["Close"]
        .dropna()
    )

    if close.empty:

        raise Exception(
            f"Nincs érvényes záróár: "
            f"{eredeti_ticker} "
            f"({yahoo_symbol})"
        )

    price = float(
        close.iloc[-1]
    )

    # ==================================================
    # DEVIZA LEKÉRÉSE
    # ==================================================

    try:

        currency = (
            instrument
            .fast_info
            .get("currency")
        )

    except Exception:

        currency = None

    # ==================================================
    # GBp / GBX → GBP
    # ==================================================
    #
    # A londoni tőzsde egyes instrumentumai
    # pennyben vannak jegyezve.
    #
    # Példa:
    #
    # EQQQ.L
    # 53869 GBp
    # =
    # 538.69 GBP
    #
    # FONTOS:
    #
    # Nem minden .L instrumentum GBp.
    #
    # Például:
    #
    # SMH.L  → USD
    # QNTM.L → USD
    #
    # Ezért NEM a ticker végződését nézzük,
    # hanem a Yahoo által megadott devizát.
    # ==================================================

    if currency in [
        "GBp",
        "GBX"
    ]:

        price = (
            price / 100
        )

    return price


# ==================================================
# TÖBB TICKER ÁRFOLYAMÁNAK LEKÉRÉSE
# ==================================================

@st.cache_data(ttl=300, show_spinner=False)
def arak_lekerese(
    tickerek
):

    arak = {}

    for ticker in tickerek:

        eredeti_ticker = str(
            ticker
        ).strip().upper()

        try:

            arak[
                eredeti_ticker
            ] = get_price(
                eredeti_ticker
            )

        except Exception as e:

            print(
                eredeti_ticker,
                "hiba:",
                e
            )

    return arak


# ==================================================
# TESZT
# ==================================================

if __name__ == "__main__":

    tickers = [
        "CSPX.L",
        "EQQQ",
        "SMH",
        "CNDX",
        "QNTM",
        "BTCN",
        "ASOL",
        "ZETH",
        "OTP"
    ]

    arak = arak_lekerese(
        tickers
    )

    print()
    print(
        "Lekért árfolyamok:"
    )
    print()

    for ticker, ar in arak.items():

        print(
            ticker,
            "-",
            ar
        )
