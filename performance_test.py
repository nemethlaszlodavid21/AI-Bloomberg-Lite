from portfolio_import import portfolio_betoltes
from portfolio_performance import portfolio_napi_teljesitmeny


portfolio = portfolio_betoltes()

eredmeny = portfolio_napi_teljesitmeny(portfolio)

for sor in eredmeny:
    print(
        sor["Eszköz"],
        ":",
        sor["Napi változás %"],
        "%"
    )