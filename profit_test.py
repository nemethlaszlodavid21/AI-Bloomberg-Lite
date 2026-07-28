from portfolio_transactions import tranzakciok_betoltese
from portfolio_profit import profit_szamitas


tranzakciok = tranzakciok_betoltese()


aktualis_arok = {

    "CSPX.L": 800,
    "EQQQ.L": 520,
    "SMH": 600,
    "BTC-USD": 70000

}


eredmeny = profit_szamitas(
    tranzakciok,
    aktualis_arok
)


print(eredmeny)