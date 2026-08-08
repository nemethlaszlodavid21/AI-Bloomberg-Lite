from portfolio_transactions import tranzakciok_betoltese
from portfolio_positions import pozicio_osszesites
from portfolio_performance_engine import teljesitmeny_szamitas
from market_data import arak_lekerese
from portfolio_import import portfolio_betoltes
from portfolio_analysis import portfolio_elemzes
from portfolio_value import portfolio_ertek_szamitas
from portfolio_risk import risk_score_szamitas

from ai_analyst import portfolio_ai_elemzes


# Portfólió

portfolio = portfolio_betoltes()

portfolio = portfolio_ertek_szamitas(
    portfolio
)

portfolio, teljes_ertek = portfolio_elemzes(
    portfolio
)


# Tranzakciók

tranzakciok = tranzakciok_betoltese()

poziciok = pozicio_osszesites(
    tranzakciok
)


# Élő árak

aktualis_arok = arak_lekerese(
    poziciok["Ticker"].tolist()
)


# Performance

performance = teljesitmeny_szamitas(
    poziciok,
    aktualis_arok
)


# Risk Score

score, szint, uzenetek = risk_score_szamitas(
    portfolio
)


# AI Analyst

elemzes = portfolio_ai_elemzes(
    portfolio,
    performance,
    score
)


print()
print("🤖 AI PORTFOLIO ANALYST")
print("=" * 40)

for uzenet in elemzes:

    print(uzenet)