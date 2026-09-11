import yfinance as yf


def stock_snapshot(ticker):

    stock = yf.Ticker(ticker)

    info = stock.info

    history = stock.history(
        period="1mo"
    )

    # ------------------------------------------------
    # ALAPADATOK
    # ------------------------------------------------

    nev = info.get(
        "longName",
        ticker
    )

    ar = info.get(
        "currentPrice"
    )

    if ar is None:

        if not history.empty:

            ar = float(
                history["Close"].iloc[-1]
            )

        else:

            ar = 0


    # ------------------------------------------------
    # NAPI VÁLTOZÁS
    # ------------------------------------------------

    previous_close = info.get(
        "previousClose"
    )

    if (
        ar is not None
        and previous_close
        and previous_close != 0
    ):

        napi_valtozas = (
            (ar / previous_close) - 1
        ) * 100

    else:

        napi_valtozas = 0


    # ------------------------------------------------
    # 30 NAPOS HOZAM
    # ------------------------------------------------

    if (
        not history.empty
        and len(history) > 1
    ):

        kezdo_ar = float(
            history["Close"].iloc[0]
        )

        vegso_ar = float(
            history["Close"].iloc[-1]
        )

        hozam_30d = (
            (vegso_ar / kezdo_ar) - 1
        ) * 100

    else:

        hozam_30d = None


    # ------------------------------------------------
    # MARKET DATA
    # ------------------------------------------------

    market_cap = info.get(
        "marketCap"
    )

    high_52w = info.get(
        "fiftyTwoWeekHigh"
    )

    low_52w = info.get(
        "fiftyTwoWeekLow"
    )


    # ------------------------------------------------
    # VALUATION
    # ------------------------------------------------

    trailing_pe = info.get(
        "trailingPE"
    )

    forward_pe = info.get(
        "forwardPE"
    )

    price_to_sales = info.get(
        "priceToSalesTrailing12Months"
    )

    price_to_book = info.get(
        "priceToBook"
    )

    ev_ebitda = info.get(
        "enterpriseToEbitda"
    )

    eps = info.get(
        "trailingEps"
    )

    dividend_yield = info.get(
        "dividendYield"
    )

    if dividend_yield is not None:

        dividend_yield = (
            dividend_yield * 100
        )


    # ------------------------------------------------
    # VALUATION SCREEN
    # ------------------------------------------------

    pontszam = 0
    meresek = 0


    # Forward P/E

    if forward_pe is not None:

        meresek += 1

        if forward_pe < 20:

            pontszam += 2

        elif forward_pe < 30:

            pontszam += 1

        elif forward_pe > 40:

            pontszam -= 1


    # Trailing P/E

    if trailing_pe is not None:

        meresek += 1

        if trailing_pe < 20:

            pontszam += 2

        elif trailing_pe < 30:

            pontszam += 1

        elif trailing_pe > 40:

            pontszam -= 1


    # Price / Sales

    if price_to_sales is not None:

        meresek += 1

        if price_to_sales < 3:

            pontszam += 2

        elif price_to_sales < 6:

            pontszam += 1

        elif price_to_sales > 10:

            pontszam -= 1


    # EV / EBITDA

    if ev_ebitda is not None:

        meresek += 1

        if ev_ebitda < 12:

            pontszam += 2

        elif ev_ebitda < 20:

            pontszam += 1

        elif ev_ebitda > 30:

            pontszam -= 1


    # ------------------------------------------------
    # ÉRTÉKELÉS
    # ------------------------------------------------

    if meresek == 0:

        valuation_status = (
            "Nincs elegendő adat"
        )

    else:

        atlag_pont = (
            pontszam / meresek
        )

        if atlag_pont >= 1.5:

            valuation_status = (
                "Attractive"
            )

        elif atlag_pont >= 0.5:

            valuation_status = (
                "Fair"
            )

        elif atlag_pont >= 0:

            valuation_status = (
                "Premium"
            )

        else:

            valuation_status = (
                "Expensive"
            )


    # ------------------------------------------------
    # RETURN
    # ------------------------------------------------

    return {

        "Ticker": ticker.upper(),

        "Név": nev,

        "Ár": ar,

        "Napi változás %":
            napi_valtozas,

        "Market Cap":
            market_cap,

        "P/E":
            trailing_pe,

        "Forward P/E":
            forward_pe,

        "P/S":
            price_to_sales,

        "P/B":
            price_to_book,

        "EV/EBITDA":
            ev_ebitda,

        "EPS":
            eps,

        "Dividend Yield %":
            dividend_yield,

        "52W High":
            high_52w,

        "52W Low":
            low_52w,

        "30D hozam %":
            hozam_30d,

        "Valuation Status":
            valuation_status
    }