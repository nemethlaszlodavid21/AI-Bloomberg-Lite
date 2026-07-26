import yfinance as yf


def get_price(ticker):
    data = yf.download(
        ticker,
        period="5d",
        progress=False
    )

    latest_price = data["Close"].dropna().iloc[-1]

    return float(latest_price.iloc[0])


if __name__ == "__main__":

    tickers = [
        "CSPX.L",
        "EQQQ.L",
        "SMH",
        "BTC-USD"
    ]

    for ticker in tickers:
        try:
            price = get_price(ticker)
            print(ticker, "-", price)

        except Exception as e:
            print(ticker, "hiba:", e)