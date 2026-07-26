# AI Bloomberg Lite
# Fő indítóprogram

from portfolio_import import portfolio_betoltes
from portfolio_analysis import portfolio_elemzes


print("================================")
print("AI Bloomberg Lite elindult")
print("================================")


portfolio = portfolio_betoltes()


print("\nBetöltött portfólió:")
print(portfolio)


portfolio, teljes_ertek = portfolio_elemzes(portfolio)


print("\nPortfólió súlyok:")

for index, sor in portfolio.iterrows():
    print(
        sor["Eszköz"],
        "-",
        round(sor["Súly %"], 2),
        "%"
    )

print("\nKockázati elemzés:")

for index, sor in portfolio.iterrows():

    if sor["Súly %"] > 40:
        print(
            "⚠️ Magas koncentráció:",
            sor["Eszköz"],
            "-",
            round(sor["Súly %"], 2),
            "%"
        )


legnagyobb = portfolio.loc[
    portfolio["Súly %"].idxmax()
]


print("\nLegnagyobb pozíció:")
print(
    legnagyobb["Eszköz"],
    "-",
    round(legnagyobb["Súly %"], 2),
    "%"
)