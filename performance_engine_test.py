from portfolio_transactions import tranzakciok_betoltese
from portfolio_positions import pozicio_osszesites
from portfolio_performance_engine import teljesitmeny_szamitas
from market_data import arak_lekerese


tranzakciok = tranzakciok_betoltese()

poziciok = pozicio_osszesites(tranzakciok)


aktualis_arok = arak_lekerese(
    poziciok["Ticker"].tolist()
)


eredmeny = teljesitmeny_szamitas(
    poziciok,
    aktualis_arok
)


print(eredmeny)