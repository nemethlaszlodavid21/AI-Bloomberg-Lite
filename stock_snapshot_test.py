from stock_snapshot import stock_snapshot


adat = stock_snapshot("AAPL")

print()
print("📊 STOCK SNAPSHOT")
print("=" * 50)

for kulcs, ertek in adat.items():
    print(f"{kulcs}: {ertek}")