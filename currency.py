import yfinance as yf


def get_currency_rate(ticker):
    adat = yf.Ticker(ticker)
    ar = adat.history(period="1d")["Close"].iloc[-1]
    
    return ar


def gbp_huf():
    return get_currency_rate("GBPHUF=X")


def usd_huf():
    return get_currency_rate("HUF=X")