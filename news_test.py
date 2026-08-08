from news_intelligence import (
    hirek_lekerese,
    hir_relevancia
)

from portfolio_import import portfolio_betoltes


portfolio = portfolio_betoltes()

hirek = hirek_lekerese()


print()
print("📰 NEWS INTELLIGENCE")
print("=" * 60)


for hir in hirek:

    eredmenyek = hir_relevancia(
        hir,
        portfolio
    )

    if eredmenyek:

        print()
        print(f"🔴 {hir['Cím']}")
        print(f"Dátum: {hir['Dátum']}")

        for eredmeny in eredmenyek:

            print(
                f"→ {eredmeny['Eszköz']} | "
                f"{eredmeny['Pontszám']} pont | "
                f"{eredmeny['Szint']}"
            )

        print(f"Link: {hir['Link']}")