import sqlite3
import uuid
from pathlib import Path

import pandas as pd


# ===================================================
# ADATBÁZIS HELYE
# ===================================================

DB_FILE = Path(__file__).with_name(
    "portfolio.db"
)


def adatbazis_fajl_beallitasa(
    db_file
):
    """
    Beállítja, hogy az aktuális felhasználói session
    melyik SQLite adatbázist használja.
    """

    global DB_FILE

    DB_FILE = Path(
        db_file
    )


# ===================================================
# ADATBÁZIS KAPCSOLAT
# ===================================================

def kapcsolat():

    conn = sqlite3.connect(
        DB_FILE
    )

    conn.row_factory = sqlite3.Row

    return conn


# ===================================================
# SEGÉDFÜGGVÉNYEK
# ===================================================

def _oszlopok_lekerese(
    conn,
    tabla
):

    rows = conn.execute(
        f"PRAGMA table_info({tabla})"
    ).fetchall()

    return {
        row["name"]
        for row in rows
    }


def _szoveg(
    ertek,
    alapertelmezett=""
):

    if pd.isna(ertek):
        return alapertelmezett

    return str(
        ertek
    ).strip()


def _float_ertek(
    ertek,
    alapertelmezett=0.0
):

    if pd.isna(ertek):
        return float(
            alapertelmezett
        )

    return float(
        ertek
    )


# ===================================================
# ADATBÁZIS INICIALIZÁLÁS + MIGRÁCIÓ
# ===================================================

def adatbazis_init():

    with kapcsolat() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                trade_date TEXT NOT NULL,

                trade_datetime TEXT,

                ticker TEXT NOT NULL,

                asset_name TEXT NOT NULL,

                side TEXT NOT NULL
                    CHECK(side IN ('BUY', 'SELL')),

                quantity REAL NOT NULL
                    CHECK(quantity > 0),

                price REAL NOT NULL
                    CHECK(price > 0),

                currency TEXT NOT NULL,

                fee REAL NOT NULL DEFAULT 0
                    CHECK(fee >= 0),

                note TEXT DEFAULT '',

                source TEXT NOT NULL
                    DEFAULT 'MANUAL',

                external_id TEXT,

                import_batch TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # -----------------------------------------------
        # RÉGI ADATBÁZIS AUTOMATIKUS MIGRÁCIÓJA
        # -----------------------------------------------

        oszlopok = _oszlopok_lekerese(
            conn,
            "transactions"
        )

        if "trade_datetime" not in oszlopok:

            conn.execute(
                """
                ALTER TABLE transactions
                ADD COLUMN trade_datetime TEXT
                """
            )

        if "source" not in oszlopok:

            conn.execute(
                """
                ALTER TABLE transactions
                ADD COLUMN source TEXT
                NOT NULL DEFAULT 'MANUAL'
                """
            )

        if "external_id" not in oszlopok:

            conn.execute(
                """
                ALTER TABLE transactions
                ADD COLUMN external_id TEXT
                """
            )

        if "import_batch" not in oszlopok:

            conn.execute(
                """
                ALTER TABLE transactions
                ADD COLUMN import_batch TEXT
                """
            )

        # -----------------------------------------------
        # IMPORT DUPLIKÁCIÓVÉDELEM
        # -----------------------------------------------

        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_transactions_source_external_id

            ON transactions (
                source,
                external_id
            )

            WHERE external_id IS NOT NULL
            """
        )

        # -----------------------------------------------
        # BEÁLLÍTÁSOK
        # -----------------------------------------------

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_settings (

                key TEXT PRIMARY KEY,

                value TEXT NOT NULL
            )
            """
        )

        conn.commit()


# ===================================================
# TRANZAKCIÓ ADAT VALIDÁLÁSA
# ===================================================

def _tranzakcio_validalas(
    ticker,
    asset_name,
    side,
    quantity,
    price,
    currency,
    fee
):

    if not ticker:

        raise ValueError(
            "A ticker megadása kötelező."
        )

    if not asset_name:

        raise ValueError(
            "Az eszköz neve kötelező."
        )

    if side not in {
        "BUY",
        "SELL"
    }:

        raise ValueError(
            "A tranzakció típusa csak BUY vagy SELL lehet."
        )

    if quantity <= 0:

        raise ValueError(
            "A darabszámnak 0-nál nagyobbnak kell lennie."
        )

    if price <= 0:

        raise ValueError(
            "Az árnak 0-nál nagyobbnak kell lennie."
        )

    if fee < 0:

        raise ValueError(
            "A tranzakciós díj nem lehet negatív."
        )

    if not currency:

        raise ValueError(
            "A deviza megadása kötelező."
        )


# ===================================================
# TRANZAKCIÓ HOZZÁADÁS
# ===================================================

def tranzakcio_hozzaadas(
    trade_date,
    ticker,
    asset_name,
    side,
    quantity,
    price,
    currency,
    fee=0.0,
    note="",
    source="MANUAL",
    external_id=None,
    import_batch=None,
    trade_datetime=None
):

    adatbazis_init()

    ticker = _szoveg(
        ticker
    ).upper()

    asset_name = _szoveg(
        asset_name
    )

    side = _szoveg(
        side
    ).upper()

    currency = _szoveg(
        currency
    ).upper()

    note = _szoveg(
        note
    )

    source = _szoveg(
        source,
        "MANUAL"
    ).upper()

    quantity = _float_ertek(
        quantity
    )

    price = _float_ertek(
        price
    )

    fee = _float_ertek(
        fee
    )

    if external_id is not None:

        external_id = _szoveg(
            external_id
        )

        if not external_id:
            external_id = None

    if import_batch is not None:

        import_batch = _szoveg(
            import_batch
        )

        if not import_batch:
            import_batch = None

    if trade_datetime is not None:

        trade_datetime = _szoveg(
            trade_datetime
        )

        if not trade_datetime:
            trade_datetime = None

    _tranzakcio_validalas(
        ticker=ticker,
        asset_name=asset_name,
        side=side,
        quantity=quantity,
        price=price,
        currency=currency,
        fee=fee
    )

    with kapcsolat() as conn:

        try:

            cursor = conn.execute(
                """
                INSERT INTO transactions (

                    trade_date,
                    trade_datetime,
                    ticker,
                    asset_name,
                    side,
                    quantity,
                    price,
                    currency,
                    fee,
                    note,
                    source,
                    external_id,
                    import_batch

                )

                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    str(
                        trade_date
                    ),
                    trade_datetime,
                    ticker,
                    asset_name,
                    side,
                    quantity,
                    price,
                    currency,
                    fee,
                    note,
                    source,
                    external_id,
                    import_batch
                )
            )

            conn.commit()

            return cursor.lastrowid

        except sqlite3.IntegrityError as hiba:

            if (
                external_id is not None
                and "UNIQUE constraint failed"
                in str(hiba)
            ):

                raise ValueError(
                    "Ez az importált tranzakció már szerepel "
                    "az adatbázisban."
                ) from hiba

            raise


# ===================================================
# TRANZAKCIÓK BETÖLTÉSE
# ===================================================

def tranzakciok_betoltese_db():

    adatbazis_init()

    query = """
        SELECT

            id,
            trade_date,
            trade_datetime,
            ticker,
            asset_name,
            side,
            quantity,
            price,
            currency,
            fee,
            note,
            source,
            external_id,
            import_batch,
            created_at

        FROM transactions

        ORDER BY

            trade_date ASC,

            CASE
                WHEN trade_datetime IS NULL THEN 1
                ELSE 0
            END ASC,

            trade_datetime ASC,

            id ASC
    """

    with kapcsolat() as conn:

        dataframe = pd.read_sql_query(
            query,
            conn
        )

    return dataframe


# ===================================================
# TRANZAKCIÓ TÖRLÉS
# ===================================================

def tranzakcio_torles(
    transaction_id
):

    adatbazis_init()

    with kapcsolat() as conn:

        conn.execute(
            """
            DELETE FROM transactions

            WHERE id = ?
            """,
            (
                int(
                    transaction_id
                ),
            )
        )

        conn.commit()


# ===================================================
# TRANZAKCIÓK SZÁMA
# ===================================================

def tranzakciok_szama():

    adatbazis_init()

    with kapcsolat() as conn:

        row = conn.execute(
            """
            SELECT COUNT(*) AS db

            FROM transactions
            """
        ).fetchone()

    return int(
        row["db"]
    )


# ===================================================
# KÉSZPÉNZ BETÖLTÉS
# ===================================================

def cash_betoltes_db():

    adatbazis_init()

    with kapcsolat() as conn:

        row = conn.execute(
            """
            SELECT value

            FROM portfolio_settings

            WHERE key = 'cash_huf'
            """
        ).fetchone()

    if row is None:

        return 0.0

    try:

        return float(
            row["value"]
        )

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# ===================================================
# KÉSZPÉNZ MENTÉS
# ===================================================

def cash_mentes_db(
    cash_huf
):

    adatbazis_init()

    cash_huf = float(
        cash_huf
    )

    if cash_huf < 0:

        raise ValueError(
            "A készpénz egyenleg nem lehet negatív."
        )

    with kapcsolat() as conn:

        conn.execute(
            """
            INSERT INTO portfolio_settings (
                key,
                value
            )

            VALUES (
                'cash_huf',
                ?
            )

            ON CONFLICT(key)

            DO UPDATE SET

                value = excluded.value
            """,
            (
                str(
                    cash_huf
                ),
            )
        )

        conn.commit()


# ===================================================
# IMPORTÁLT TRANZAKCIÓ LÉTEZIK-E
# ===================================================

def import_tranzakcio_letezik(
    source,
    external_id
):

    adatbazis_init()

    source = _szoveg(
        source
    ).upper()

    external_id = _szoveg(
        external_id
    )

    if (
        not source
        or not external_id
    ):

        return False

    with kapcsolat() as conn:

        row = conn.execute(
            """
            SELECT id

            FROM transactions

            WHERE source = ?
              AND external_id = ?

            LIMIT 1
            """,
            (
                source,
                external_id
            )
        ).fetchone()

    return row is not None


# ===================================================
# RÉGI KOMPATIBILITÁS
# ===================================================

def tranzakcio_letezik(
    trade_date,
    ticker,
    side,
    quantity,
    price,
    currency,
    fee=0.0
):

    adatbazis_init()

    ticker = _szoveg(
        ticker
    ).upper()

    side = _szoveg(
        side
    ).upper()

    currency = _szoveg(
        currency
    ).upper()

    quantity = _float_ertek(
        quantity
    )

    price = _float_ertek(
        price
    )

    fee = _float_ertek(
        fee
    )

    with kapcsolat() as conn:

        row = conn.execute(
            """
            SELECT id

            FROM transactions

            WHERE trade_date = ?
              AND ticker = ?
              AND side = ?
              AND ABS(quantity - ?) < 0.00000001
              AND ABS(price - ?) < 0.00000001
              AND currency = ?
              AND ABS(fee - ?) < 0.00000001

            LIMIT 1
            """,
            (
                str(
                    trade_date
                ),
                ticker,
                side,
                quantity,
                price,
                currency,
                fee
            )
        ).fetchone()

    return row is not None


# ===================================================
# IMPORT SOR NORMALIZÁLÁSA
# ===================================================

def _import_sor_normalizalas(
    sor,
    batch_id
):

    trade_date = _szoveg(
        sor["datum"]
    )

    ticker = _szoveg(
        sor["ticker"]
    ).upper()

    asset_name = _szoveg(
        sor.get(
            "eszkoz_nev",
            ticker
        )
    )

    if not asset_name:
        asset_name = ticker

    side = _szoveg(
        sor["tipus"]
    ).upper()

    quantity = _float_ertek(
        sor["mennyiseg"]
    )

    price = _float_ertek(
        sor["ar"]
    )

    currency = _szoveg(
        sor["deviza"]
    ).upper()

    fee = _float_ertek(
        sor.get(
            "jutalek",
            0.0
        )
    )

    note = _szoveg(
        sor.get(
            "megjegyzes",
            ""
        )
    )

    source = _szoveg(
        sor.get(
            "forras",
            "IMPORT"
        ),
        "IMPORT"
    ).upper()

    external_id = _szoveg(
        sor.get(
            "import_id",
            ""
        )
    )

    if not external_id:

        raise ValueError(
            f"{ticker}: az importazonosító hiányzik."
        )

    trade_datetime = _szoveg(
        sor.get(
            "datum_ido",
            ""
        )
    )

    if not trade_datetime:
        trade_datetime = None

    _tranzakcio_validalas(
        ticker=ticker,
        asset_name=asset_name,
        side=side,
        quantity=quantity,
        price=price,
        currency=currency,
        fee=fee
    )

    return {
        "trade_date": trade_date,
        "trade_datetime": trade_datetime,
        "ticker": ticker,
        "asset_name": asset_name,
        "side": side,
        "quantity": quantity,
        "price": price,
        "currency": currency,
        "fee": fee,
        "note": note,
        "source": source,
        "external_id": external_id,
        "import_batch": batch_id
    }


# ===================================================
# TÖMEGES TRANZAKCIÓ IMPORT
# ===================================================

def tranzakciok_importalasa_db(
    tranzakciok
):

    adatbazis_init()

    eredmeny = {
        "osszes": 0,
        "importalt": 0,
        "duplikalt": 0,
        "hibas": 0,
        "hibak": [],
        "batch_id": None
    }

    if (
        tranzakciok is None
        or tranzakciok.empty
    ):

        return eredmeny

    eredmeny["osszes"] = len(
        tranzakciok
    )

    batch_id = str(
        uuid.uuid4()
    )

    eredmeny[
        "batch_id"
    ] = batch_id

    normalizalt = []

    # -----------------------------------------------
    # 1. TELJES IMPORT VALIDÁLÁSA MEMÓRIÁBAN
    # -----------------------------------------------

    for index, sor in tranzakciok.iterrows():

        try:

            adat = _import_sor_normalizalas(
                sor,
                batch_id
            )

            normalizalt.append(
                adat
            )

        except Exception as hiba:

            eredmeny[
                "hibas"
            ] += 1

            eredmeny[
                "hibak"
            ].append(
                f"{index}: {hiba}"
            )

    # -----------------------------------------------
    # HA EGYETLEN HIBÁS SOR VAN:
    # SEMMIT NEM IMPORTÁLUNK
    # -----------------------------------------------

    if eredmeny["hibas"] > 0:

        return eredmeny

    # -----------------------------------------------
    # 2. ATOMI IMPORT
    # -----------------------------------------------

    try:

        with kapcsolat() as conn:

            for adat in normalizalt:

                letezik = conn.execute(
                    """
                    SELECT id

                    FROM transactions

                    WHERE source = ?
                      AND external_id = ?

                    LIMIT 1
                    """,
                    (
                        adat["source"],
                        adat["external_id"]
                    )
                ).fetchone()

                if letezik is not None:

                    eredmeny[
                        "duplikalt"
                    ] += 1

                    continue

                conn.execute(
                    """
                    INSERT INTO transactions (

                        trade_date,
                        trade_datetime,
                        ticker,
                        asset_name,
                        side,
                        quantity,
                        price,
                        currency,
                        fee,
                        note,
                        source,
                        external_id,
                        import_batch

                    )

                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        adat["trade_date"],
                        adat["trade_datetime"],
                        adat["ticker"],
                        adat["asset_name"],
                        adat["side"],
                        adat["quantity"],
                        adat["price"],
                        adat["currency"],
                        adat["fee"],
                        adat["note"],
                        adat["source"],
                        adat["external_id"],
                        adat["import_batch"]
                    )
                )

                eredmeny[
                    "importalt"
                ] += 1

            conn.commit()

    except Exception as hiba:

        # A context manager rollbackolja az egész batch-et.

        eredmeny[
            "importalt"
        ] = 0

        eredmeny[
            "hibas"
        ] += 1

        eredmeny[
            "hibak"
        ].append(
            str(
                hiba
            )
        )

    return eredmeny  