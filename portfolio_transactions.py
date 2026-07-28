import pandas as pd


def tranzakciok_betoltese():

    return pd.read_csv(
        "data/transactions.csv"
    )