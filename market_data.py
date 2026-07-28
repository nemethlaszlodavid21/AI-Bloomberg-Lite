import yfinance as yf
import pandas as pd


def get_price(ticker):

    data = yf.download(
        ticker,
        period="5d",
        progress=False,
        auto_adjust=True
    )

    if data.empty:
        raise Exception("Nincs adat")


    if isinstance(data.columns, pd.MultiIndex):
        close = data["Close"][ticker]

    else:
        close = data["Close"]


    price = float(close.dropna().iloc[-1])


    # London Stock Exchange GBX -> GBP
    if ticker.endswith(".L") and price > 10000:
        price = price / 100


    return price



def arak_lekerese(tickerek):

    arak = {}

    for ticker in tickerek:

        try:
            arak[ticker] = get_price(ticker)

        except Exception as e:
            print(
                ticker,
                "hiba:",
                e
            )

    return arak



if __name__ == "__main__":

    tickers = [
        "CSPX.L",
        "EQQQ.L",
        "SMH",
        "BTC-USD"
    ]


    arak = arak_lekerese(tickers)


    for ticker, ar in arak.items():

        print(
            ticker,
            "-",
            ar
        )