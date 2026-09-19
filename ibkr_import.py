import csv
import io
import hashlib
import pandas as pd


# --------------------------------------------------
# SEGÉDFÜGGVÉNYEK
# --------------------------------------------------

def _szam_konvertalas(ertek):
    """
    IBKR számszöveg -> float.

    Példák:
    "12.5"   -> 12.5
    "-3"     -> -3.0
    "-1,385" -> -1385.0
    """

    if ertek is None:
        return None

    szoveg = str(ertek).strip()

    if szoveg == "":
        return None

    szoveg = szoveg.replace(",", "")

    try:
        return float(szoveg)
    except ValueError:
        return None


def _fajl_szoveg_beolvasasa(fajl):
    """
    Kezeli:
    - Streamlit UploadedFile objektumot
    - bytes adatot
    - normál fájlobjektumot
    """

    if hasattr(fajl, "getvalue"):
        adat = fajl.getvalue()

    elif isinstance(fajl, bytes):
        adat = fajl

    elif hasattr(fajl, "read"):
        adat = fajl.read()

    else:
        raise ValueError(
            "Nem támogatott fájlformátum."
        )

    if isinstance(adat, str):
        return adat

    kodolasok = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin1",
    ]

    for kodolas in kodolasok:
        try:
            return adat.decode(kodolas)
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "A CSV karakterkódolása nem olvasható."
    )


def _tranzakcio_hash(
    datum,
    ticker,
    tipus,
    mennyiseg,
    ar,
    deviza,
    jutalek,
):
    """
    Stabil azonosító egy importált tranzakcióhoz.

    Később ezt használhatjuk a
    duplikált importok kiszűrésére.
    """

    kulcs = "|".join(
        [
            str(datum),
            str(ticker).upper(),
            str(tipus).upper(),
            f"{float(mennyiseg):.10f}",
            f"{float(ar):.10f}",
            str(deviza).upper(),
            f"{float(jutalek):.10f}",
        ]
    )

    return hashlib.sha256(
        kulcs.encode("utf-8")
    ).hexdigest()


# --------------------------------------------------
# IBKR CSV FELISMERÉS
# --------------------------------------------------

def ibkr_csv_ellenorzes(fajl):
    """
    Megvizsgálja, hogy a feltöltött fájl
    tartalmaz-e értelmezhető IBKR Ügyletek
    szekciót.
    """

    try:
        szoveg = _fajl_szoveg_beolvasasa(
            fajl
        )

        reader = csv.reader(
            io.StringIO(szoveg)
        )

        for sor in reader:

            if (
                len(sor) >= 6
                and sor[0] == "Ügyletek"
                and sor[1] == "Header"
                and "Ticker kód" in sor
                and "Mennyiség" in sor
                and "Ügyleti ár" in sor
            ):
                return True

        return False

    except Exception:
        return False


# --------------------------------------------------
# IBKR TRANZAKCIÓK FELDOLGOZÁSA
# --------------------------------------------------

def ibkr_tranzakciok_feldolgozasa(fajl):
    """
    IBKR Activity Statement CSV feldolgozása.

    Jelenleg támogatott:
    Ügyletek
        -> Data
        -> Order
        -> Részvények

    Nem importáljuk:
    - Deviza ügyleteket
    - SubTotal sorokat
    - Total sorokat
    """

    szoveg = _fajl_szoveg_beolvasasa(
        fajl
    )

    reader = csv.reader(
        io.StringIO(szoveg)
    )

    fejléc = None
    tranzakciok = []

    for sor in reader:

        if not sor:
            continue

        # ------------------------------------------
        # ÜGYLETEK FEJLÉC
        # ------------------------------------------

        if (
            len(sor) >= 6
            and sor[0] == "Ügyletek"
            and sor[1] == "Header"
        ):

            fejléc = sor
            continue

        # ------------------------------------------
        # CSAK VALÓDI ORDER SOROK
        # ------------------------------------------

        if (
            len(sor) < 4
            or sor[0] != "Ügyletek"
            or sor[1] != "Data"
            or sor[2] != "Order"
            or sor[3] != "Részvények"
        ):
            continue

        if fejléc is None:
            continue

        # ------------------------------------------
        # SOR -> DICT
        # ------------------------------------------

        rekord = {}

        for index, oszlop in enumerate(fejléc):

            if index < len(sor):
                rekord[oszlop] = sor[index]
            else:
                rekord[oszlop] = ""

        ticker = (
            rekord
            .get("Ticker kód", "")
            .strip()
            .upper()
        )

        deviza = (
            rekord
            .get("Deviza", "")
            .strip()
            .upper()
        )

        datum_ido = (
            rekord
            .get("Dátum / Idő", "")
            .strip()
        )

        mennyiseg_raw = _szam_konvertalas(
            rekord.get("Mennyiség")
        )

        ar = _szam_konvertalas(
            rekord.get("Ügyleti ár")
        )

        jutalek_raw = _szam_konvertalas(
            rekord.get("Jut./díj")
        )

        # ------------------------------------------
        # VALIDÁCIÓ
        # ------------------------------------------

        if (
            not ticker
            or not datum_ido
            or mennyiseg_raw is None
            or mennyiseg_raw == 0
            or ar is None
            or ar <= 0
        ):
            continue

        # ------------------------------------------
        # BUY / SELL
        # ------------------------------------------

        if mennyiseg_raw > 0:
            tipus = "BUY"
        else:
            tipus = "SELL"

        mennyiseg = abs(
            mennyiseg_raw
        )

        # IBKR-ben a jutalék jellemzően negatív.
        # A saját adatbázisban pozitív költségként
        # tároljuk.
        jutalek = abs(
            jutalek_raw or 0.0
        )

        # ------------------------------------------
        # DÁTUM
        # ------------------------------------------

        try:
            datum_obj = pd.to_datetime(
                datum_ido.split(",")[0],
                format="%Y-%m-%d"
            )

            datum = (
                datum_obj
                .strftime("%Y-%m-%d")
            )

        except Exception:
            continue

        # ------------------------------------------
        # TRANZAKCIÓ AZONOSÍTÓ
        # ------------------------------------------

        import_id = _tranzakcio_hash(
            datum=datum_ido,
            ticker=ticker,
            tipus=tipus,
            mennyiseg=mennyiseg,
            ar=ar,
            deviza=deviza,
            jutalek=jutalek,
        )

        # ------------------------------------------
        # EGYSÉGES TRANZAKCIÓ
        # ------------------------------------------

        tranzakciok.append(
            {
                "datum": datum,
                "datum_ido": datum_ido,
                "ticker": ticker,
                "eszkoz_nev": ticker,
                "tipus": tipus,
                "mennyiseg": mennyiseg,
                "ar": ar,
                "deviza": deviza,
                "jutalek": jutalek,
                "megjegyzes": "IBKR import",
                "forras": "IBKR",
                "import_id": import_id,
            }
        )

    if not tranzakciok:
        return pd.DataFrame(
            columns=[
                "datum",
                "datum_ido",
                "ticker",
                "eszkoz_nev",
                "tipus",
                "mennyiseg",
                "ar",
                "deviza",
                "jutalek",
                "megjegyzes",
                "forras",
                "import_id",
            ]
        )

    df = pd.DataFrame(
        tranzakciok
    )

    df = (
        df
        .sort_values(
            by=[
                "datum_ido",
                "ticker",
            ]
        )
        .reset_index(drop=True)
    )

    return df


# --------------------------------------------------
# IMPORT ÖSSZEFOGLALÓ
# --------------------------------------------------

def ibkr_import_osszefoglalo(tranzakciok):
    """
    Import előnézethez szükséges
    összesítő adatok.
    """

    if (
        tranzakciok is None
        or tranzakciok.empty
    ):
        return {
            "tranzakciok_szama": 0,
            "buy_db": 0,
            "sell_db": 0,
            "ticker_db": 0,
            "devizak": [],
            "kezdo_datum": None,
            "veg_datum": None,
        }

    return {
        "tranzakciok_szama":
            len(tranzakciok),

        "buy_db":
            int(
                (
                    tranzakciok["tipus"]
                    == "BUY"
                ).sum()
            ),

        "sell_db":
            int(
                (
                    tranzakciok["tipus"]
                    == "SELL"
                ).sum()
            ),

        "ticker_db":
            int(
                tranzakciok[
                    "ticker"
                ].nunique()
            ),

        "devizak":
            sorted(
                tranzakciok[
                    "deviza"
                ]
                .dropna()
                .unique()
                .tolist()
            ),

        "kezdo_datum":
            tranzakciok[
                "datum"
            ].min(),

        "veg_datum":
            tranzakciok[
                "datum"
            ].max(),
    }