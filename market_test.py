import yfinance as yf

adat = yf.download(
    "AAPL",
    period="5d",
    progress=False
)

print(adat)