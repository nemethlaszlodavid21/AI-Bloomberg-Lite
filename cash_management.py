import json
from pathlib import Path


CASH_FILE = Path(__file__).with_name(
    "cash_balance.json"
)


def cash_betoltes():

    if not CASH_FILE.exists():
        return 0.0

    try:

        with open(
            CASH_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            adat = json.load(file)

        return float(
            adat.get(
                "cash_huf",
                0
            )
        )

    except Exception:

        return 0.0


def cash_mentes(cash_huf):

    adat = {
        "cash_huf": float(cash_huf)
    }

    with open(
        CASH_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            adat,
            file,
            indent=4
        )


def cash_mutatok(
    befektetett_ertek_huf,
    cash_huf
):

    teljes_portfolio = (
        befektetett_ertek_huf
        + cash_huf
    )

    if teljes_portfolio > 0:

        cash_szazalek = (
            cash_huf
            / teljes_portfolio
            * 100
        )

        invested_szazalek = (
            befektetett_ertek_huf
            / teljes_portfolio
            * 100
        )

    else:

        cash_szazalek = 0
        invested_szazalek = 0

    return {
        "Teljes portfólió": teljes_portfolio,
        "Befektetett tőke": befektetett_ertek_huf,
        "Cash": cash_huf,
        "Cash %": cash_szazalek,
        "Invested %": invested_szazalek,
        "Available capital": cash_huf
    }