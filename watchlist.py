import streamlit as st
import yfinance as yf


ALAP_WATCHLIST = [
    "NVDA",
    "AAPL",
    "MSFT",
    "TSLA",
    "AMD",
    "META"
]


@st.cache_data(ttl=300, show_spinner=False)
def watchlist_lekerese(tickerek=None):

    if tickerek is None:
        tickerek = ALAP_WATCHLIST

    tickerek = [
        str(t).strip().upper()
        for t in tickerek
        if str(t).strip()
    ]

    if not tickerek:
        return []

    try:
        adat = yf.download(
            tickerek,
            period="5d",
            progress=False,
            auto_adjust=True,
            group_by="column",
            threads=True
        )
    except Exception:
        return []

    if adat is None or adat.empty:
        return []

    eredmeny = []

    for ticker in tickerek:
        try:
            if isinstance(adat.columns, __import__("pandas").MultiIndex):
                zaras = adat["Close"][ticker].dropna()
            else:
                zaras = adat["Close"].dropna()

            if len(zaras) < 2:
                continue

            aktualis = float(zaras.iloc[-1])
            elozo = float(zaras.iloc[-2])
            valtozas = ((aktualis - elozo) / elozo) * 100

            eredmeny.append({
                "Ticker": ticker,
                "Ár": aktualis,
                "Napi változás %": valtozas
            })
        except Exception:
            continue

    return eredmeny
