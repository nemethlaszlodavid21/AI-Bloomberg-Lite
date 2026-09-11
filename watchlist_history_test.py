from watchlist_history import watchlist_tortenet


adatok = watchlist_tortenet("AAPL")

print()
print("📈 AAPL - 30 NAPOS ÁRFOLYAM")
print("=" * 50)

print(adatok.tail(10))