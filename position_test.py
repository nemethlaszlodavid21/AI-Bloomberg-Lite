from portfolio_transactions import tranzakciok_betoltese
from portfolio_positions import pozicio_osszesites


tranzakciok = tranzakciok_betoltese()

poziciok = pozicio_osszesites(tranzakciok)

print(poziciok)