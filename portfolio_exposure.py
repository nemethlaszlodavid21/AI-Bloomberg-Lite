import pandas as pd


def _theme_besorolas(eszköz):

    nev = str(eszköz).upper()

    if "BTC" in nev or "BITCOIN" in nev:
        return "Crypto"

    if "SMH" in nev:
        return "Semiconductors"

    if (
        "EQQQ" in nev
        or "QQQ" in nev
    ):
        return "Technology"

    if (
        "CSPX" in nev
        or "SPY" in nev
        or "VOO" in nev
        or "IVV" in nev
    ):
        return "Broad US Equity"

    return "Other"


def _asset_class_besorolas(eszköz):

    nev = str(eszköz).upper()

    if "BTC" in nev or "BITCOIN" in nev:
        return "Crypto"

    if (
        "CSPX" in nev
        or "EQQQ" in nev
        or "QQQ" in nev
        or "SMH" in nev
        or "SPY" in nev
        or "VOO" in nev
        or "IVV" in nev
    ):
        return "Equity ETF"

    return "Other"


def _exposure_osszesites(
    dataframe,
    kategori_oszlop,
    ertek_oszlop="HUF érték"
):

    osszes_ertek = dataframe[
        ertek_oszlop
    ].sum()

    exposure = (
        dataframe
        .groupby(
            kategori_oszlop,
            as_index=False
        )[ertek_oszlop]
        .sum()
    )

    if osszes_ertek > 0:

        exposure["Súly %"] = (
            exposure[ertek_oszlop]
            / osszes_ertek
            * 100
        )

    else:

        exposure["Súly %"] = 0

    exposure = exposure.sort_values(
        "Súly %",
        ascending=False
    )

    return exposure


def portfolio_exposure_szamitas(
    portfolio
):

    adat = portfolio.copy()

    adat["Theme"] = adat[
        "Eszköz"
    ].apply(
        _theme_besorolas
    )

    adat["Asset Class"] = adat[
        "Eszköz"
    ].apply(
        _asset_class_besorolas
    )

    theme_exposure = (
        _exposure_osszesites(
            adat,
            "Theme"
        )
    )

    currency_exposure = (
        _exposure_osszesites(
            adat,
            "Deviza"
        )
    )

    asset_class_exposure = (
        _exposure_osszesites(
            adat,
            "Asset Class"
        )
    )

    return (
        theme_exposure,
        currency_exposure,
        asset_class_exposure
    )