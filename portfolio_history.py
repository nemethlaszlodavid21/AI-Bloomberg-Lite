import pandas as pd
import yfinance as yf

from fx_data import historikus_huf_arfolyam


# ===================================================
# SEGÉDFÜGGVÉNYEK
# ===================================================

def _ures_tortenet():

    return pd.DataFrame(
        columns=[
            "Portfolio"
        ]
    )


def _ticker_historikus_arak(
    ticker,
    start_date,
    end_date
):

    try:

        adat = yf.download(
            ticker,
            start=start_date.strftime(
                "%Y-%m-%d"
            ),
            end=(
                end_date
                + pd.Timedelta(days=1)
            ).strftime(
                "%Y-%m-%d"
            ),
            auto_adjust=True,
            progress=False
        )

    except Exception:

        return pd.Series(
            dtype=float
        )


    if adat.empty:

        return pd.Series(
            dtype=float
        )


    if isinstance(
        adat.columns,
        pd.MultiIndex
    ):

        adat.columns = (
            adat.columns
            .get_level_values(0)
        )


    if "Close" not in adat.columns:

        return pd.Series(
            dtype=float
        )


    close = (
        adat["Close"]
        .dropna()
        .copy()
    )


    close.index = (
        pd.to_datetime(
            close.index
        )
        .tz_localize(None)
        .normalize()
    )


    return close


def _fx_historikus_arak(
    deviza,
    start_date,
    end_date
):

    deviza = (
        str(deviza)
        .strip()
        .upper()
    )


    if deviza == "HUF":

        index = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )

        return pd.Series(
            1.0,
            index=index,
            dtype=float
        )


    fx_tickerek = {

        "USD": "USDHUF=X",

        "EUR": "EURHUF=X",

        "GBP": "GBPHUF=X",

        "CHF": "CHFHUF=X"
    }


    if deviza not in fx_tickerek:

        return pd.Series(
            dtype=float
        )


    ticker = (
        fx_tickerek[
            deviza
        ]
    )


    try:

        adat = yf.download(
            ticker,
            start=(
                start_date
                - pd.Timedelta(days=10)
            ).strftime(
                "%Y-%m-%d"
            ),
            end=(
                end_date
                + pd.Timedelta(days=1)
            ).strftime(
                "%Y-%m-%d"
            ),
            auto_adjust=False,
            progress=False
        )

    except Exception:

        return pd.Series(
            dtype=float
        )


    if adat.empty:

        return pd.Series(
            dtype=float
        )


    if isinstance(
        adat.columns,
        pd.MultiIndex
    ):

        adat.columns = (
            adat.columns
            .get_level_values(0)
        )


    if "Close" not in adat.columns:

        return pd.Series(
            dtype=float
        )


    close = (
        adat["Close"]
        .dropna()
        .copy()
    )


    close.index = (
        pd.to_datetime(
            close.index
        )
        .tz_localize(None)
        .normalize()
    )


    return close


# ===================================================
# TRANZAKCIÓ-ALAPÚ PORTFÓLIÓ TÖRTÉNET
# ===================================================

def portfolio_tortenet(
    portfolio,
    tranzakciok=None
):

    # -----------------------------------------------
    # VISSZAFELÉ KOMPATIBILITÁS
    # -----------------------------------------------
    #
    # Ha nincs tranzakciós adat,
    # nem próbálunk mai pozíciókat visszavetíteni
    # a múltba.
    # -----------------------------------------------

    if (
        tranzakciok is None
        or tranzakciok.empty
    ):

        return _ures_tortenet()


    tx = (
        tranzakciok
        .copy()
    )


    kotelezo_oszlopok = {

        "trade_date",

        "ticker",

        "side",

        "quantity",

        "currency"
    }


    if not kotelezo_oszlopok.issubset(
        tx.columns
    ):

        return _ures_tortenet()


    # -----------------------------------------------
    # TRANZAKCIÓK TISZTÍTÁSA
    # -----------------------------------------------

    tx["trade_date"] = (
        pd.to_datetime(
            tx["trade_date"],
            errors="coerce"
        )
        .dt
        .normalize()
    )


    tx = (
        tx
        .dropna(
            subset=[
                "trade_date"
            ]
        )
    )


    if tx.empty:

        return _ures_tortenet()


    tx["ticker"] = (
        tx["ticker"]
        .astype(str)
        .str
        .strip()
        .str
        .upper()
    )


    tx["side"] = (
        tx["side"]
        .astype(str)
        .str
        .strip()
        .str
        .upper()
    )


    tx["currency"] = (
        tx["currency"]
        .astype(str)
        .str
        .strip()
        .str
        .upper()
    )


    tx["quantity"] = (
        pd.to_numeric(
            tx["quantity"],
            errors="coerce"
        )
    )


    tx = (
        tx
        .dropna(
            subset=[
                "quantity"
            ]
        )
    )


    if tx.empty:

        return _ures_tortenet()


    # -----------------------------------------------
    # IDŐSZAK
    # -----------------------------------------------

    start_date = (
        tx["trade_date"]
        .min()
    )


    end_date = (
        pd.Timestamp.today()
        .tz_localize(None)
        .normalize()
    )


    if start_date > end_date:

        return _ures_tortenet()


    # -----------------------------------------------
    # NAPI INDEX
    # -----------------------------------------------
    #
    # BDays:
    # hétfő-péntek.
    #
    # Az eltérő tőzsdei ünnepnapokat később
    # az árfolyamok forward fillje kezeli.
    # -----------------------------------------------

    napok = pd.date_range(
        start=start_date,
        end=end_date,
        freq="B"
    )


    if len(napok) == 0:

        return _ures_tortenet()


    portfolio_napi = pd.DataFrame(
        index=napok
    )


    # -----------------------------------------------
    # TICKERENKÉNTI POZÍCIÓ
    # -----------------------------------------------

    tickerek = (
        tx["ticker"]
        .dropna()
        .unique()
        .tolist()
    )


    for ticker in tickerek:

        ticker_tx = (
            tx[
                tx["ticker"]
                == ticker
            ]
            .copy()
        )


        if ticker_tx.empty:

            continue


        devizak = (
            ticker_tx[
                "currency"
            ]
            .dropna()
            .unique()
            .tolist()
        )


        if len(devizak) != 1:

            continue


        deviza = (
            devizak[0]
        )


        # -------------------------------------------
        # NAPI DARABSZÁM-VÁLTOZÁS
        # -------------------------------------------

        ticker_tx[
            "quantity_change"
        ] = ticker_tx.apply(
            lambda sor:
                float(
                    sor["quantity"]
                )
                if sor["side"] == "BUY"
                else
                -float(
                    sor["quantity"]
                ),
            axis=1
        )


        napi_valtozas = (
            ticker_tx
            .groupby(
                "trade_date"
            )[
                "quantity_change"
            ]
            .sum()
        )


        napi_valtozas = (
            napi_valtozas
            .reindex(
                napok,
                fill_value=0.0
            )
        )


        napi_darab = (
            napi_valtozas
            .cumsum()
        )


        # -------------------------------------------
        # HISTORIKUS ESZKÖZÁR
        # -------------------------------------------

        arak = (
            _ticker_historikus_arak(
                ticker,
                start_date,
                end_date
            )
        )


        if arak.empty:

            continue


        arak = (
            arak
            .reindex(
                napok
            )
            .ffill()
        )


        # -------------------------------------------
        # HISTORIKUS FX
        # -------------------------------------------

        fx = (
            _fx_historikus_arak(
                deviza,
                start_date,
                end_date
            )
        )


        if fx.empty:

            continue


        fx = (
            fx
            .reindex(
                napok
            )
            .ffill()
        )


        # -------------------------------------------
        # HUF POZÍCIÓÉRTÉK
        # -------------------------------------------

        pozicio_ertek_huf = (
            napi_darab
            * arak
            * fx
        )


        pozicio_ertek_huf = (
            pozicio_ertek_huf
            .fillna(0.0)
        )


        portfolio_napi[
            ticker
        ] = pozicio_ertek_huf


    # -----------------------------------------------
    # HA NINCS HASZNÁLHATÓ ADAT
    # -----------------------------------------------

    if portfolio_napi.empty:

        return _ures_tortenet()


    # -----------------------------------------------
    # PORTFÓLIÓ PIACI ÉRTÉK HUF
    # -----------------------------------------------

    portfolio_napi[
        "Portfolio"
    ] = (
        portfolio_napi
        .sum(
            axis=1
        )
    )


    # -----------------------------------------------
    # TRANZAKCIÓ ELŐTTI NULLA NAPOK KISZŰRÉSE
    # -----------------------------------------------

    portfolio_napi = (
        portfolio_napi[
            portfolio_napi[
                "Portfolio"
            ] > 0
        ]
    )


    if portfolio_napi.empty:

        return _ures_tortenet()


    # -----------------------------------------------
    # CASH-FLOW-SEMLEGES NAPI HOZAM
    # -----------------------------------------------
    #
    # A nyers portfólióérték változását nem használjuk
    # közvetlenül hozamként, mert egy új BUY tranzakció
    # mesterséges ugrást okozna.
    #
    # Az adott napi hozamot az előző napi pozíciók
    # piaci árfolyamváltozásából számoljuk.
    # -----------------------------------------------

    napi_pnl = pd.Series(
        0.0,
        index=portfolio_napi.index,
        dtype=float
    )

    elozo_napi_ertek = pd.Series(
        0.0,
        index=portfolio_napi.index,
        dtype=float
    )

    for ticker in tickerek:

        ticker_tx = (
            tx[
                tx["ticker"] == ticker
            ]
            .copy()
        )

        if ticker_tx.empty:
            continue

        devizak = (
            ticker_tx["currency"]
            .dropna()
            .unique()
            .tolist()
        )

        if len(devizak) != 1:
            continue

        deviza = devizak[0]

        ticker_tx["quantity_change"] = (
            ticker_tx.apply(
                lambda sor:
                    float(sor["quantity"])
                    if sor["side"] == "BUY"
                    else -float(sor["quantity"]),
                axis=1
            )
        )

        napi_valtozas = (
            ticker_tx
            .groupby("trade_date")["quantity_change"]
            .sum()
            .reindex(
                napok,
                fill_value=0.0
            )
        )

        napi_darab = (
            napi_valtozas
            .cumsum()
        )

        elozo_napi_darab = (
            napi_darab
            .shift(1)
            .fillna(0.0)
        )

        arak = _ticker_historikus_arak(
            ticker,
            start_date - pd.Timedelta(days=7),
            end_date
        )

        if arak.empty:
            continue

        arak = (
            arak
            .reindex(napok)
            .ffill()
        )

        fx = _fx_historikus_arak(
            deviza,
            start_date - pd.Timedelta(days=7),
            end_date
        )

        if fx.empty:
            continue

        fx = (
            fx
            .reindex(napok)
            .ffill()
        )

        huf_ar = (
            arak * fx
        )

        elozo_huf_ar = (
            huf_ar
            .shift(1)
        )

        ticker_napi_pnl = (
            elozo_napi_darab
            * (
                huf_ar
                - elozo_huf_ar
            )
        ).fillna(0.0)

        ticker_elozo_ertek = (
            elozo_napi_darab
            * elozo_huf_ar
        ).fillna(0.0)

        napi_pnl = (
            napi_pnl
            .add(
                ticker_napi_pnl,
                fill_value=0.0
            )
        )

        elozo_napi_ertek = (
            elozo_napi_ertek
            .add(
                ticker_elozo_ertek,
                fill_value=0.0
            )
        )

    napi_hozam = pd.Series(
        0.0,
        index=portfolio_napi.index,
        dtype=float
    )

    ervenyes = (
        elozo_napi_ertek > 0
    )

    napi_hozam.loc[ervenyes] = (
        napi_pnl.loc[ervenyes]
        / elozo_napi_ertek.loc[ervenyes]
    )

    portfolio_napi["Daily Return"] = (
        napi_hozam
    )

    return portfolio_napi
