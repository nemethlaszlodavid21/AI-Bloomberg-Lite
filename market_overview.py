import yfinance as yf


MARKET_ESZKOZOK = {
    "S&P 500": {
        "ticker": "^GSPC",
        "tipus": "index"
    },
    "Nasdaq 100": {
        "ticker": "^NDX",
        "tipus": "index"
    },
    "VIX": {
        "ticker": "^VIX",
        "tipus": "vix"
    },
    "US 10Y": {
        "ticker": "^TNX",
        "tipus": "yield"
    },
    "Gold": {
        "ticker": "GC=F",
        "tipus": "price"
    },
    "Bitcoin": {
        "ticker": "BTC-USD",
        "tipus": "price"
    }
}


def market_overview_lekerese():

    eredmenyek = []

    for nev, adat in MARKET_ESZKOZOK.items():

        ticker = adat["ticker"]
        tipus = adat["tipus"]

        try:

            stock = yf.Ticker(ticker)

            history = stock.history(
                period="5d"
            )

            if history.empty:
                continue

            history = history.dropna(
                subset=["Close"]
            )

            if history.empty:
                continue

            aktualis_ar = float(
                history["Close"].iloc[-1]
            )

            if len(history) >= 2:

                elozo_ar = float(
                    history["Close"].iloc[-2]
                )

                napi_valtozas = (
                    (
                        aktualis_ar
                        / elozo_ar
                    ) - 1
                ) * 100

            else:

                napi_valtozas = 0


            eredmenyek.append(
                {
                    "Név": nev,
                    "Ticker": ticker,
                    "Érték": aktualis_ar,
                    "Napi változás %": napi_valtozas,
                    "Típus": tipus
                }
            )

        except Exception as e:

            print(
                f"Hiba a(z) {ticker} lekérésekor: {e}"
            )

    return eredmenyek