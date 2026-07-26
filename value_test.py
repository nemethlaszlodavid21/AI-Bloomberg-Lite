import pandas as pd

from portfolio_value import portfolio_ertek_szamitas


portfolio = pd.read_csv("data/portfolio.csv")


eredmeny = portfolio_ertek_szamitas(portfolio)


print(eredmeny)

print("\nTeljes érték:")
print(eredmeny["Pozíció érték"].sum())