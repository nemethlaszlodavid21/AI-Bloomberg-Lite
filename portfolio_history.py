import pandas as pd
import yfinance as yf

from market_data import yahoo_ticker
from corporate_actions import ticker_corporate_actions


# ===================================================
# ÜRES PORTFÓLIÓ TÖRTÉNET
# ===================================================

def _ures_tortenet():

    return pd.DataFrame(
        columns=[
            "Portfolio",
            "Daily Return"
        ]
    )


# ===================================================
# HISTORIKUS TICKER ÁRAK
# ===================================================

def _ticker_historikus_arak(
    ticker,
    start_date,
    end_date
):

    # --------------------------------------------------
    # IBKR → YAHOO MAPPING
    # --------------------------------------------------

    yahoo_symbol = yahoo_ticker(
        ticker
    )

    try:

        instrument = yf.Ticker(
            yahoo_symbol
        )

        adat = instrument.history(
            start=start_date.strftime(
                "%Y-%m-%d"
            ),
            end=(
                end_date
                + pd.Timedelta(days=1)
            ).strftime(
                "%Y-%m-%d"
            ),
            auto_adjust=True
        )

    except Exception:

        return pd.Series(
            dtype=float
        )

    if adat.empty:

        return pd.Series(
            dtype=float
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

    # ==================================================
    # YAHOO DEVIZA
    # ==================================================

    try:

        currency = (
            instrument
            .fast_info
            .get("currency")
        )

    except Exception:

        currency = None

    # ==================================================
    # GBp / GBX → GBP
    # ==================================================

    if currency in {
        "GBp",
        "GBX"
    }:

        close = (
            close / 100
        )

    return close


# ===================================================
# HISTORIKUS FX
# ===================================================

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

    ticker = fx_tickerek[
        deviza
    ]

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
# CORPORATE ACTIONÖKKEL KORRIGÁLT NAPI DARABSZÁM
# ===================================================

def _napi_darabszam(
    ticker,
    ticker_tx,
    napok
):

    # --------------------------------------------------
    # TRANZAKCIÓS DARABSZÁMVÁLTOZÁS
    # --------------------------------------------------

    ticker_tx = ticker_tx.copy()

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

    # ==================================================
    # CORPORATE ACTIONÖK
    # ==================================================

    actions = ticker_corporate_actions(
        ticker
    )

    # --------------------------------------------------
    # NAPONKÉNT ÉPÍTJÜK FEL A POZÍCIÓT
    # --------------------------------------------------
    #
    # Ez azért fontos, mert:
    #
    # BUY 940 IMUX
    #
    # majd:
    #
    # 1:10 reverse split
    #
    # után:
    #
    # 94 IMUX
    #
    # Ha később újabb BUY/SELL történik,
    # az már a split utáni darabszámhoz adódik.
    # --------------------------------------------------

    darab = 0.0

    napi_darab = pd.Series(
        0.0,
        index=napok,
        dtype=float
    )

    for datum in napok:

        # ----------------------------------------------
        # CORPORATE ACTION
        # ----------------------------------------------

        if not actions.empty:

            napi_actions = actions[
                actions["date"].dt.normalize()
                == datum
            ]

            for _, action in (
                napi_actions.iterrows()
            ):

                action_type = str(
                    action["type"]
                ).strip().upper()

                if action_type != "SPLIT":
                    continue

                ratio = float(
                    action["split_ratio"]
                )

                if ratio <= 0:
                    continue

                darab *= ratio

        # ----------------------------------------------
        # TRANZAKCIÓ
        # ----------------------------------------------

        if datum in napi_valtozas.index:

            darab += float(
                napi_valtozas.loc[
                    datum
                ]
            )

        # ----------------------------------------------
        # RÉSZLEGES IBKR TÖRTÉNET
        # ----------------------------------------------
        #
        # Ha a CSV olyan SELL-lel kezdődik,
        # amelynek BUY tranzakciója a CSV kezdete
        # előtt történt, nem engedjük, hogy a
        # historikus pozíció negatív legyen.
        # ----------------------------------------------

        if darab < 0:

            darab = 0.0

        napi_darab.loc[
            datum
        ] = darab

    return napi_darab


# ===================================================
# TRANZAKCIÓ-ALAPÚ PORTFÓLIÓ TÖRTÉNET
# ===================================================

def portfolio_tortenet(
    portfolio,
    tranzakciok=None
):

    # ==================================================
    # VISSZAFELÉ KOMPATIBILITÁS
    # ==================================================
    #
    # Az app jelenleg így hívhatja:
    #
    # portfolio_tortenet(
    #     portfolio,
    #     tranzakciok
    # )
    #
    # Ezért megtartjuk mindkét paramétert.
    # ==================================================

    if (
        tranzakciok is None
        or tranzakciok.empty
    ):

        return _ures_tortenet()

    tx = tranzakciok.copy()

    kotelezo_oszlopok = {

        "trade_date",

        "ticker",

        "side",

        "quantity",

        "currency"
    }

    if not kotelezo_oszopok_check(
        tx,
        kotelezo_oszlopok
    ):

        return _ures_tortenet()

    # ==================================================
    # TRANZAKCIÓK TISZTÍTÁSA
    # ==================================================

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

    # ==================================================
    # IDŐSZAK
    # ==================================================

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

    # ==================================================
    # NAPI INDEX
    # ==================================================

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

    # ==================================================
    # MARKET P/L
    # ==================================================

    market_pnl = pd.Series(
        0.0,
        index=napok,
        dtype=float
    )

    elozo_napi_ertek = pd.Series(
        0.0,
        index=napok,
        dtype=float
    )

    # ==================================================
    # TICKEREK
    # ==================================================

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

        deviza = devizak[0]

        # ==================================================
        # NAPI DARABSZÁM
        # ==================================================

        napi_darab = _napi_darabszam(
            ticker,
            ticker_tx,
            napok
        )

        # ==================================================
        # HISTORIKUS ÁRAK
        # ==================================================

        arak = _ticker_historikus_arak(
            ticker,
            start_date,
            end_date
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

        # ==================================================
        # HISTORIKUS FX
        # ==================================================

        fx = _fx_historikus_arak(
            deviza,
            start_date,
            end_date
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

        # ==================================================
        # HUF ÁRFOLYAM
        # ==================================================

        ar_huf = (
            arak
            * fx
        )

        # ==================================================
        # POZÍCIÓÉRTÉK
        # ==================================================

        pozicio_ertek_huf = (
            napi_darab
            * ar_huf
        )

        pozicio_ertek_huf = (
            pozicio_ertek_huf
            .fillna(0.0)
        )

        portfolio_napi[
            ticker
        ] = pozicio_ertek_huf

        # ==================================================
        # CASH-FLOW SEMLEGES MARKET P/L
        # ==================================================
        #
        # A mai ármozgást a TEGNAPI darabszámmal
        # számoljuk.
        #
        # BUY / SELL ezért nem jelenik meg
        # mesterséges napi hozamként.
        # ==================================================

        elozo_darab = (
            napi_darab
            .shift(1)
            .fillna(0.0)
        )

        elozo_ar_huf = (
            ar_huf
            .shift(1)
        )

        ticker_market_pnl = (
            elozo_darab
            * (
                ar_huf
                - elozo_ar_huf
            )
        )

        ticker_market_pnl = (
            ticker_market_pnl
            .fillna(0.0)
        )

        market_pnl = (
            market_pnl
            + ticker_market_pnl
        )

        ticker_start_value = (
            elozo_darab
            * elozo_ar_huf
        )

        ticker_start_value = (
            ticker_start_value
            .fillna(0.0)
        )

        elozo_napi_ertek = (
            elozo_napi_ertek
            + ticker_start_value
        )

    # ==================================================
    # HA NINCS HASZNÁLHATÓ ADAT
    # ==================================================

    if portfolio_napi.empty:

        return _ures_tortenet()

    # ==================================================
    # PORTFÓLIÓ PIACI ÉRTÉK
    # ==================================================

    portfolio_napi[
        "Portfolio"
    ] = (
        portfolio_napi
        .sum(
            axis=1
        )
    )

    # ==================================================
    # DAILY RETURN
    # ==================================================
    #
    # market P/L
    # -----------------
    # előző napi érték
    #
    # Nem használunk sima Portfolio.pct_change()-et,
    # mert a BUY / SELL tranzakciók cash flow-k,
    # nem befektetési hozamok.
    # ==================================================

    daily_return = pd.Series(
        0.0,
        index=napok,
        dtype=float
    )

    ervenyes = (
        elozo_napi_ertek
        > 0
    )

    daily_return.loc[
        ervenyes
    ] = (
        market_pnl.loc[
            ervenyes
        ]
        / elozo_napi_ertek.loc[
            ervenyes
        ]
    )

    daily_return = (
        daily_return
        .replace(
            [
                float("inf"),
                float("-inf")
            ],
            pd.NA
        )
        .fillna(0.0)
    )

    portfolio_napi[
        "Daily Return"
    ] = daily_return

    # ==================================================
    # TRANZAKCIÓ ELŐTTI NULLA NAPOK KISZŰRÉSE
    # ==================================================

    portfolio_napi = (
        portfolio_napi[
            portfolio_napi[
                "Portfolio"
            ] > 0
        ]
    )

    if portfolio_napi.empty:

        return _ures_tortenet()

    return portfolio_napi


# ===================================================
# KÖTELEZŐ OSZLOPOK ELLENŐRZÉSE
# ===================================================

def kotelezo_oszopok_check(
    dataframe,
    kotelezo_oszlopok
):

    return kotelezo_oszlopok.issubset(
        dataframe.columns
    )