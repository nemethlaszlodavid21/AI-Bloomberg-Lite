from watchlist import watchlist_lekerese


adatok = watchlist_lekerese()


print()
print("👀 WATCHLIST")
print("=" * 40)

for adat in adatok:

    print(

        f"{adat['Ticker']} | "
        f"{adat['Ár']:.2f} | "
        f"{adat['Napi változás %']:.2f}%"

    )