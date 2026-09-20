from __future__ import annotations

from datetime import timedelta

import pandas as pd
import yfinance as yf


FX_TICKERS = {
    "USD": "USDHUF=X",
    "EUR": "EURHUF=X",
    "GBP": "GBPHUF=X",
    "CHF": "CHFHUF=X",
}


def historikus_fx_adatok(deviza: str, kezdo_datum, veg_datum):
    deviza = str(deviza).upper().strip()

    if deviza == "HUF":
        return None

    ticker = FX_TICKERS.get(deviza)
    if ticker is None:
        raise ValueError(f"Nem támogatott deviza: {deviza}")

    kezdo = pd.Timestamp(kezdo_datum).normalize()
    veg = pd.Timestamp(veg_datum).normalize() + timedelta(days=5)

    adat = yf.download(
        ticker,
        start=kezdo.strftime("%Y-%m-%d"),
        end=veg.strftime("%Y-%m-%d"),
        auto_adjust=False,
        progress=False,
    )

    if adat is None or adat.empty:
        raise ValueError(f"Nem érkezett FX adat ehhez: {deviza}/HUF")

    close = adat["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = pd.to_numeric(close, errors="coerce").dropna()
    close.index = pd.to_datetime(close.index).tz_localize(None).normalize()

    if close.empty:
        raise ValueError(f"Nincs használható FX záróár ehhez: {deviza}/HUF")

    return close.sort_index()


def fx_arfolyam_kereses(datum, deviza: str, fx_adatok):
    deviza = str(deviza).upper().strip()

    if deviza == "HUF":
        return 1.0

    if fx_adatok is None or len(fx_adatok) == 0:
        return None

    datum = pd.Timestamp(datum).tz_localize(None).normalize()
    elozo = fx_adatok.loc[fx_adatok.index <= datum]

    if not elozo.empty:
        return float(elozo.iloc[-1])

    kesobbi = fx_adatok.loc[fx_adatok.index > datum]
    if not kesobbi.empty:
        return float(kesobbi.iloc[0])

    return None


def tranzakcios_koltsegek_elemzese(tranzakciok: pd.DataFrame) -> dict:
    ures = {
        "osszes_dij_huf": 0.0,
        "atlag_dij_huf": 0.0,
        "tranzakciok_szama": 0,
        "dijak_devizankent": {},
        "buy_forgalom_huf": 0.0,
        "koltseghanyad_pct": None,
        "fx_lefedettseg_pct": 100.0,
        "fx_hianyzo_devizak": [],
        "reszletek": pd.DataFrame(),
    }

    if tranzakciok is None or tranzakciok.empty:
        return ures

    kotelezo = {"trade_date", "currency", "fee", "side", "quantity", "price"}
    hianyzo = kotelezo - set(tranzakciok.columns)
    if hianyzo:
        raise ValueError(
            "A tranzakciós költségelemzéshez hiányzó oszlopok: "
            + ", ".join(sorted(hianyzo))
        )

    df = tranzakciok.copy()
    df["trade_date"] = pd.to_datetime(df["trade_date"], errors="coerce").dt.normalize()
    df["currency"] = df["currency"].fillna("HUF").astype(str).str.upper().str.strip()
    df["side"] = df["side"].fillna("").astype(str).str.upper().str.strip()
    df["fee"] = pd.to_numeric(df["fee"], errors="coerce").fillna(0.0).abs()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["trade_date"])

    if df.empty:
        return ures

    kezdo = df["trade_date"].min() - pd.Timedelta(days=7)
    veg = df["trade_date"].max()

    devizak = sorted(df["currency"].dropna().unique().tolist())
    fx_cache = {}
    hianyzo_devizak = []

    for deviza in devizak:
        if deviza == "HUF":
            fx_cache[deviza] = None
            continue
        try:
            fx_cache[deviza] = historikus_fx_adatok(deviza, kezdo, veg)
        except Exception:
            fx_cache[deviza] = None
            hianyzo_devizak.append(deviza)

    fee_huf = []
    for _, sor in df.iterrows():
        fx = fx_arfolyam_kereses(
            sor["trade_date"], sor["currency"], fx_cache.get(sor["currency"])
        )
        fee_huf.append(float(sor["fee"]) * fx if fx is not None else None)

    df["fee_huf"] = fee_huf

    # BUY forgalom: quantity × price, az adott tranzakció napjának FX-ével HUF-ra váltva.
    df["gross_value"] = df["quantity"].abs() * df["price"].abs()
    gross_huf = []
    for _, sor in df.iterrows():
        if sor["side"] != "BUY":
            gross_huf.append(None)
            continue
        fx = fx_arfolyam_kereses(
            sor["trade_date"], sor["currency"], fx_cache.get(sor["currency"])
        )
        gross_huf.append(float(sor["gross_value"]) * fx if fx is not None else None)

    df["buy_gross_huf"] = gross_huf

    dijas = df["fee"] > 0
    dijas_db = int(dijas.sum())
    konvertalt_dijas_db = int((dijas & df["fee_huf"].notna()).sum())
    fx_lefedettseg = (
        konvertalt_dijas_db / dijas_db * 100.0 if dijas_db > 0 else 100.0
    )

    osszes_dij_huf = float(df["fee_huf"].dropna().sum())
    tranzakciok_szama = int(len(df))
    atlag_dij_huf = (
        osszes_dij_huf / tranzakciok_szama if tranzakciok_szama > 0 else 0.0
    )

    buy_forgalom_huf = float(df.loc[df["side"] == "BUY", "buy_gross_huf"].dropna().sum())
    koltseghanyad_pct = (
        osszes_dij_huf / buy_forgalom_huf * 100.0
        if buy_forgalom_huf > 0 and fx_lefedettseg >= 99.999
        else None
    )

    dijak_devizankent = (
        df.groupby("currency", dropna=False)["fee"]
        .sum()
        .sort_index()
        .to_dict()
    )

    return {
        "osszes_dij_huf": osszes_dij_huf,
        "atlag_dij_huf": atlag_dij_huf,
        "tranzakciok_szama": tranzakciok_szama,
        "dijak_devizankent": dijak_devizankent,
        "buy_forgalom_huf": buy_forgalom_huf,
        "koltseghanyad_pct": koltseghanyad_pct,
        "fx_lefedettseg_pct": fx_lefedettseg,
        "fx_hianyzo_devizak": sorted(set(hianyzo_devizak)),
        "reszletek": df,
    }
