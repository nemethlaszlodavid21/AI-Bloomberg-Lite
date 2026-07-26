import pandas as pd

from portfolio_market import get_market_price
from currency import gbp_huf, usd_huf


def portfolio_ertek_szamitas(df):

    eredmeny = []

    gbp = gbp_huf()
    usd = usd_huf()

    for index, sor in df.iterrows():

        ticker = sor["Ticker"]
        darab = sor["Darab"]

        ar = get_market_price(ticker)

        if ticker.endswith(".L"):
            huf_ar = ar * gbp
            deviza = "GBP"

        elif ticker == "BTC-USD" or ticker == "SMH":
            huf_ar = ar * usd
            deviza = "USD"

        else:
            huf_ar = ar
            deviza = "HUF"


        ertek = darab * huf_ar


        eredmeny.append({
            "Eszköz": sor["Eszköz"],
            "Ticker": ticker,
            "Darab": darab,
            "Deviza": deviza,
            "Ár": ar,
            "HUF érték": ertek
        })


    return pd.DataFrame(eredmeny)