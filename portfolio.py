# AI Bloomberg Lite - Portfolio Analyzer v0.3

def portfolio_elemzes(eszkozok, ertekek):

    osszes_vagyon = sum(ertekek)

    print("Teljes portfólió érték:", osszes_vagyon, "Ft")
    print("\nPortfólió elemzés:")

    for i in range(len(eszkozok)):

        suly = ertekek[i] / osszes_vagyon * 100

        print(eszkozok[i], "-", round(suly, 2), "%")

        if suly > 40:
            print("⚠️ Magas koncentráció:", eszkozok[i])


# Portfólió adatok

eszkozok = ["CSPX", "EQQQ", "SMH", "BTC"]

ertekek = [1500000, 800000, 500000, 200000]


# Elemzés indítása

portfolio_elemzes(eszkozok, ertekek)