import streamlit as st
import yfinance as yf
import pandas as pd


@st.cache_data(ttl=900, show_spinner=False)
def watchlist_tortenet(ticker, period="30d"):

    adat = yf.download(
        ticker,
        period=period,
        progress=False,
        auto_adjust=True
    )

    if adat.empty:
        raise Exception(f"Nincs elérhető adat ehhez: {ticker}")

    if isinstance(adat.columns, pd.MultiIndex):
        close = adat["Close"][ticker]
    else:
        close = adat["Close"]

    close = close.dropna()

    eredmeny = pd.DataFrame({
        "Dátum": close.index,
        "Ár": close.values
    })

    return eredmeny
