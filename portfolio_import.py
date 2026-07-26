import pandas as pd
from pathlib import Path


def portfolio_betoltes():

    projekt_mappa = Path(__file__).parent

    csv_fajl = projekt_mappa / "data" / "portfolio.csv"

    df = pd.read_csv(csv_fajl)

    return df