import yfinance as yf


def napi_valtozas(ticker):

    adat = yf.Ticker(ticker)

    tortenet = adat.history(period="2d")

    if len(tortenet) < 2:
        return 0

    tegnapi_zaras = tortenet["Close"].iloc[-2]
    mai_ar = tortenet["Close"].iloc[-1]

    valtozas = (mai_ar - tegnapi_zaras) / tegnapi_zaras

    return valtozas

def portfolio_napi_teljesitmeny(portfolio):

    eredmenyek = []

    for index, sor in portfolio.iterrows():

        ticker = sor["Ticker"]

        valtozas = napi_valtozas(ticker)

        eredmenyek.append({
            "Eszköz": sor["Eszköz"],
            "Ticker": ticker,
            "Napi változás %": round(valtozas * 100, 2)
        })

    return eredmenyek