import pandas as pd
from portfolio_market import get_market_price


def portfolio_ertek_szamitas(df):

    eredmeny = []

    for index, sor in df.iterrows():

        ticker = sor["Ticker"]
        darab = sor["Darab"]

        ar = get_market_price(ticker)

        ertek = darab * ar

        eredmeny.append({
            "Eszköz": sor["Eszköz"],
            "Ticker": ticker,
            "Darab": darab,
            "Aktuális ár": ar,
            "Pozíció érték": ertek
        })

    return pd.DataFrame(eredmeny)