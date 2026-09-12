import sqlite3
from pathlib import Path

import pandas as pd


DB_FILE = Path(__file__).with_name(
    "portfolio.db"
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
# ADATBÁZIS INICIALIZÁLÁS
# ===================================================

def adatbazis_init():

    with kapcsolat() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                trade_date TEXT NOT NULL,

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

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


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
    note=""
):

    adatbazis_init()


    ticker = str(
        ticker
    ).strip().upper()


    asset_name = str(
        asset_name
    ).strip()


    side = str(
        side
    ).strip().upper()


    currency = str(
        currency
    ).strip().upper()


    note = str(
        note
    ).strip()


    quantity = float(
        quantity
    )


    price = float(
        price
    )


    fee = float(
        fee
    )


    # -----------------------------------------------
    # VALIDÁLÁS
    # -----------------------------------------------

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


    # -----------------------------------------------
    # MENTÉS
    # -----------------------------------------------

    with kapcsolat() as conn:

        cursor = conn.execute(
            """
            INSERT INTO transactions (

                trade_date,
                ticker,
                asset_name,
                side,
                quantity,
                price,
                currency,
                fee,
                note

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(
                    trade_date
                ),

                ticker,

                asset_name,

                side,

                quantity,

                price,

                currency,

                fee,

                note
            )
        )


        conn.commit()


        return cursor.lastrowid


# ===================================================
# TRANZAKCIÓK BETÖLTÉSE
# ===================================================

def tranzakciok_betoltese_db():

    adatbazis_init()


    query = """
        SELECT

            id,
            trade_date,
            ticker,
            asset_name,
            side,
            quantity,
            price,
            currency,
            fee,
            note,
            created_at

        FROM transactions

        ORDER BY

            trade_date ASC,
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