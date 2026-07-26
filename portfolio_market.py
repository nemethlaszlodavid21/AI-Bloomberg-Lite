import yfinance as yf


def get_market_price(ticker):

    data = yf.download(
        ticker,
        period="5d",
        progress=False
    )

    price = data["Close"].dropna().iloc[-1]

    return round(float(price.iloc[0]), 2)