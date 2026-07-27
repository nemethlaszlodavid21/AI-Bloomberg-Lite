import yfinance as yf
import pandas as pd


def portfolio_tortenet(portfolio):

    tortenet = pd.DataFrame()

    for index, sor in portfolio.iterrows():

        ticker = sor["Ticker"]
        darab = sor["Darab"]

        adat = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )

        if adat.empty:
            continue

        if isinstance(adat.columns, pd.MultiIndex):
            adat.columns = adat.columns.get_level_values(0)

        adat["Ertek"] = adat["Close"] * darab

        eszkoz = sor["Eszköz"]

        tortenet[eszkoz] = adat["Ertek"]


    tortenet["Portfolio"] = tortenet.sum(axis=1)

    return tortenet