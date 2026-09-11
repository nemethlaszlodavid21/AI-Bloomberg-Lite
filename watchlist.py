import yfinance as yf


ALAP_WATCHLIST = [
    "NVDA",
    "AAPL",
    "MSFT",
    "TSLA",
    "AMD",
    "META"
]


def watchlist_lekerese(tickerek=None):

    if tickerek is None:
        tickerek = ALAP_WATCHLIST

    eredmeny = []

    for ticker in tickerek:

        try:

            adat = yf.download(
                ticker,
                period="5d",
                progress=False,
                auto_adjust=True
            )

            if adat.empty:
                continue

            zaras = adat["Close"]

            if hasattr(zaras, "columns"):
                zaras = zaras[ticker]

            aktualis = float(zaras.iloc[-1])
            elozo = float(zaras.iloc[-2])

            valtozas = (
                (aktualis - elozo)
                / elozo
            ) * 100

            eredmeny.append({
                "Ticker": ticker,
                "Ár": aktualis,
                "Napi változás %": valtozas
            })

        except Exception:

            continue

    return eredmeny