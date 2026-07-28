import pandas as pd


def profit_szamitas(tranzakciok, aktualis_arok):

    eredmeny = []

    for index, sor in tranzakciok.iterrows():

        ticker = sor["Ticker"]
        darab = sor["Darab"]
        veteli_ar = sor["Vételi ár"]

        bekerules = darab * veteli_ar

        aktualis_ar = aktualis_arok[ticker]

        aktualis_ertek = darab * aktualis_ar

        profit = aktualis_ertek - bekerules

        hozam = (profit / bekerules) * 100


        eredmeny.append({

            "Eszköz": sor["Eszköz"],
            "Ticker": ticker,
            "Bekerülési érték": bekerules,
            "Aktuális érték": aktualis_ertek,
            "Profit": profit,
            "Hozam %": hozam

        })


    return pd.DataFrame(eredmeny)