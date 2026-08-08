from news_intelligence import (
    hirek_lekerese,
    hir_relevancia
)

from portfolio_import import portfolio_betoltes

from ai_news import hir_ai_elemzes


portfolio = portfolio_betoltes()

hirek = hirek_lekerese()


print()
print("🤖 AI NEWS INTELLIGENCE")
print("=" * 60)


for hir in hirek:

    relevanciak = hir_relevancia(
        hir,
        portfolio
    )

    if not relevanciak:
        continue

    print()
    print("📰", hir["Cím"])

    print()

    elemzes = hir_ai_elemzes(
        hir,
        relevanciak
    )

    print(elemzes)

    print()
    print("-" * 60)