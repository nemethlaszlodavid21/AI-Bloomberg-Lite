import pandas as pd


def pozicio_osszesites(tranzakciok):

    poziciok = []

    csoportok = tranzakciok.groupby(
        ["Eszköz", "Ticker", "Deviza"]
    )

    for (eszkoz, ticker, deviza), adat in csoportok:

        darab = adat["Darab"].sum()

        bekerules = (
            adat["Darab"] * adat["Vételi ár"]
        ).sum()

        atlag_ar = bekerules / darab

        poziciok.append({

            "Eszköz": eszkoz,
            "Ticker": ticker,
            "Deviza": deviza,
            "Darab": darab,
            "Átlag vételi ár": atlag_ar,
            "Bekerülési érték": bekerules

        })


    return pd.DataFrame(poziciok)