import yfinance as yf


def stock_snapshot(ticker):

    reszveny = yf.Ticker(ticker)

    info = reszveny.info

    tortenet = reszveny.history(period="1y")

    if tortenet.empty:
        raise Exception(f"Nincs elérhető adat ehhez: {ticker}")

    aktualis_ar = float(tortenet["Close"].iloc[-1])

    elozo_ar = float(tortenet["Close"].iloc[-2])

    napi_valtozas = (
        (aktualis_ar - elozo_ar)
        / elozo_ar
    ) * 100

    high_52w = float(tortenet["High"].max())

    low_52w = float(tortenet["Low"].min())

    if len(tortenet) >= 22:

        ar_30_nappal_ezelott = float(
            tortenet["Close"].iloc[-22]
        )

        hozam_30d = (
            (aktualis_ar - ar_30_nappal_ezelott)
            / ar_30_nappal_ezelott
        ) * 100

    else:
        hozam_30d = None

    eredmeny = {
        "Ticker": ticker,
        "Név": info.get("longName", ticker),
        "Ár": aktualis_ar,
        "Napi változás %": napi_valtozas,
        "Market Cap": info.get("marketCap"),
        "P/E": info.get("trailingPE"),
        "52W High": high_52w,
        "52W Low": low_52w,
        "30D hozam %": hozam_30d
    }

    return eredmeny