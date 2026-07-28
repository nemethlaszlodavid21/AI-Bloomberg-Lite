import pandas as pd


def teljesitmeny_szamitas(poziciok, aktualis_arok):

    eredmeny = []

    for index, sor in poziciok.iterrows():

        ticker = sor["Ticker"]
        darab = sor["Darab"]
        bekerules = sor["Bekerülési érték"]

        aktualis_ar = aktualis_arok[ticker]

        aktualis_ertek = darab * aktualis_ar

        profit = aktualis_ertek - bekerules

        hozam = (profit / bekerules) * 100


        eredmeny.append({

            "Eszköz": sor["Eszköz"],
            "Ticker": ticker,
            "Darab": darab,
            "Bekerülési érték": bekerules,
            "Aktuális érték": aktualis_ertek,
            "Profit": profit,
            "Hozam %": hozam

        })


    return pd.DataFrame(eredmeny)