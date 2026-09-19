import pandas as pd


# ==================================================
# CORPORATE ACTION ADATBÁZIS
# ==================================================
#
# A tranzakciós adatbázist NEM módosítjuk.
#
# A corporate action eseményeket külön kezeljük,
# így az eredeti broker tranzakciók változatlanok
# maradnak.
#
# split_ratio:
#
# 2:1 split
#   → 2.0
#
# 1:10 reverse split
#   → 0.1
#
# ==================================================

CORPORATE_ACTIONS = [

    {
        "ticker": "IMUX",
        "date": "2026-04-27",
        "type": "SPLIT",
        "split_ratio": 0.1,
        "description": "1:10 reverse stock split",
    },

]


# ==================================================
# CORPORATE ACTION DATAFRAME
# ==================================================

def corporate_actions_dataframe():

    df = pd.DataFrame(
        CORPORATE_ACTIONS
    )

    if df.empty:
        return df

    df["date"] = pd.to_datetime(
        df["date"]
    )

    return df.sort_values(
        "date"
    ).reset_index(
        drop=True
    )


# ==================================================
# TICKER CORPORATE ACTIONJEI
# ==================================================

def ticker_corporate_actions(
    ticker
):

    ticker = str(
        ticker
    ).strip().upper()

    df = corporate_actions_dataframe()

    if df.empty:
        return df

    return (
        df[
            df["ticker"].str.upper()
            == ticker
        ]
        .copy()
        .reset_index(drop=True)
    )


# ==================================================
# MENNYISÉG SPLIT KORREKCIÓ
# ==================================================

def adjust_quantity_for_splits(
    ticker,
    quantity,
    from_date,
    to_date=None
):

    ticker = str(
        ticker
    ).strip().upper()

    quantity = float(
        quantity
    )

    from_date = pd.Timestamp(
        from_date
    )

    if to_date is None:

        to_date = pd.Timestamp.now()

    else:

        to_date = pd.Timestamp(
            to_date
        )

    actions = ticker_corporate_actions(
        ticker
    )

    if actions.empty:
        return quantity

    relevant_actions = actions[
        (actions["date"] > from_date)
        &
        (actions["date"] <= to_date)
        &
        (actions["type"] == "SPLIT")
    ]

    adjusted_quantity = quantity

    for _, action in (
        relevant_actions.iterrows()
    ):

        adjusted_quantity *= float(
            action["split_ratio"]
        )

    return adjusted_quantity


# ==================================================
# ÁTLAGÁR SPLIT KORREKCIÓ
# ==================================================

def adjust_price_for_splits(
    ticker,
    price,
    from_date,
    to_date=None
):

    ticker = str(
        ticker
    ).strip().upper()

    price = float(
        price
    )

    from_date = pd.Timestamp(
        from_date
    )

    if to_date is None:

        to_date = pd.Timestamp.now()

    else:

        to_date = pd.Timestamp(
            to_date
        )

    actions = ticker_corporate_actions(
        ticker
    )

    if actions.empty:
        return price

    relevant_actions = actions[
        (actions["date"] > from_date)
        &
        (actions["date"] <= to_date)
        &
        (actions["type"] == "SPLIT")
    ]

    adjusted_price = price

    for _, action in (
        relevant_actions.iterrows()
    ):

        ratio = float(
            action["split_ratio"]
        )

        if ratio == 0:
            continue

        adjusted_price /= ratio

    return adjusted_price


# ==================================================
# TESZT
# ==================================================

if __name__ == "__main__":

    eredeti_db = 940
    eredeti_ar = 0.850842553

    datum = "2026-02-24"

    uj_db = adjust_quantity_for_splits(
        ticker="IMUX",
        quantity=eredeti_db,
        from_date=datum
    )

    uj_ar = adjust_price_for_splits(
        ticker="IMUX",
        price=eredeti_ar,
        from_date=datum
    )

    print()
    print("IMUX corporate action teszt")
    print("---------------------------")

    print(
        "Eredeti darabszám:",
        eredeti_db
    )

    print(
        "Split-adjustált darabszám:",
        uj_db
    )

    print(
        "Eredeti bekerülési ár:",
        eredeti_ar
    )

    print(
        "Split-adjustált bekerülési ár:",
        uj_ar
    )

    print(
        "Eredeti bekerülési érték:",
        eredeti_db * eredeti_ar
    )

    print(
        "Split-adjustált bekerülési érték:",
        uj_db * uj_ar
    )