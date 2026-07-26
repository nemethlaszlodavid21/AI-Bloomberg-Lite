import yfinance as yf


import yfinance as yf


def get_market_price(ticker):

    adat = yf.Ticker(ticker)

    ar = adat.history(period="1d")["Close"].iloc[-1]

    # Londoni tőzsde penny → font korrekció
    if ticker.endswith(".L") and ar > 10000:
        ar = ar / 100

    return ar