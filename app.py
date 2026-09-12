import pandas as pd
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go


from portfolio_value import (
    portfolio_ertek_szamitas
)

from portfolio_analysis import (
    portfolio_elemzes
)

from portfolio_performance import (
    portfolio_napi_teljesitmeny
)

from portfolio_risk import (
    risk_score_szamitas
)

from portfolio_history import (
    portfolio_tortenet
)

from portfolio_benchmark import (
    benchmark_osszehasonlitas,
    benchmark_hozamok
)

from portfolio_exposure import (
    portfolio_exposure_szamitas
)

from portfolio_holdings import (
    holdings_tabla_keszites
)

from etf_lookthrough import (
    portfolio_lookthrough
)

from risk_analytics import (
    risk_analytics_szamitas,
    drawdown_idosor
)

from portfolio_database import (
    adatbazis_init,
    tranzakcio_hozzaadas,
    tranzakciok_betoltese_db,
    tranzakcio_torles,
    cash_betoltes_db,
    cash_mentes_db
)

from portfolio_engine import (
    poziciok_szamitas_db,
    portfolio_adatframe_db,
    performance_szamitas_db
)

from market_data import (
    arak_lekerese
)

from market_overview import (
    market_overview_lekerese
)

from ai_analyst import (
    portfolio_ai_elemzes
)

from watchlist import (
    watchlist_lekerese
)

from watchlist_history import (
    watchlist_tortenet
)

from stock_snapshot import (
    stock_snapshot
)

from style import (
    alkalmaz_style
)


# ===================================================
# PAGE CONFIG
# ===================================================

st.set_page_config(
    page_title="AI Bloomberg Lite",
    page_icon="📈",
    layout="wide"
)


alkalmaz_style()


# ===================================================
# ADATBÁZIS
# ===================================================

adatbazis_init()


db_tranzakciok = (
    tranzakciok_betoltese_db()
)


van_tranzakcio = (
    not db_tranzakciok.empty
)


# ===================================================
# HEADER
# ===================================================

st.title(
    "AI Bloomberg Lite"
)


st.caption(
    "Portfólióelemzés • Piaci információk • Részvényelemzés"
)


# ===================================================
# PORTFÓLIÓ FORRÁS
# CSAK SQLITE
# ===================================================

if van_tranzakcio:

    try:

        db_poziciok = (
            poziciok_szamitas_db(
                db_tranzakciok
            )
        )


        portfolio = (
            portfolio_adatframe_db(
                db_tranzakciok
            )
        )


    except Exception as e:

        st.error(
            f"Hiba a tranzakciós napló feldolgozásakor: {e}"
        )


        st.stop()


else:

    db_poziciok = pd.DataFrame(
        columns=[
            "Eszköz",
            "Ticker",
            "Darab",
            "Deviza",
            "Átlagár",
            "Bekerülési érték",
            "Realizált P/L"
        ]
    )


    portfolio = pd.DataFrame(
        columns=[
            "Eszköz",
            "Ticker",
            "Darab",
            "Deviza"
        ]
    )


# ===================================================
# PORTFÓLIÓ ÉRTÉK
# ===================================================

if not portfolio.empty:

    portfolio = (
        portfolio_ertek_szamitas(
            portfolio
        )
    )


    portfolio, teljes_ertek = (
        portfolio_elemzes(
            portfolio
        )
    )


else:

    portfolio[
        "HUF érték"
    ] = pd.Series(
        dtype=float
    )


    portfolio[
        "Súly %"
    ] = pd.Series(
        dtype=float
    )


    teljes_ertek = 0.0


# ===================================================
# LEGNAGYOBB POZÍCIÓ
# ===================================================

if not portfolio.empty:

    legnagyobb = (
        portfolio.loc[
            portfolio[
                "Súly %"
            ].idxmax()
        ]
    )

else:

    legnagyobb = None


# ===================================================
# KÉSZPÉNZ
# SZINTÉN SQLITE
# ===================================================

cash_huf = (
    cash_betoltes_db()
)


teljes_portfolio_ertek = (
    teljes_ertek
    + cash_huf
)


if teljes_portfolio_ertek > 0:

    cash_szazalek = (
        cash_huf
        / teljes_portfolio_ertek
        * 100
    )

else:

    cash_szazalek = 0.0


# ===================================================
# EXPOSURE
# ===================================================

if not portfolio.empty:

    try:

        (
            _,
            currency_exposure,
            asset_class_exposure
        ) = (
            portfolio_exposure_szamitas(
                portfolio
            )
        )


    except Exception:

        currency_exposure = (
            pd.DataFrame()
        )

        asset_class_exposure = (
            pd.DataFrame()
        )


    try:

        sector_exposure = (
            portfolio_lookthrough(
                portfolio
            )
        )

    except Exception:

        sector_exposure = (
            pd.DataFrame()
        )


else:

    currency_exposure = (
        pd.DataFrame()
    )


    asset_class_exposure = (
        pd.DataFrame()
    )


    sector_exposure = (
        pd.DataFrame()
    )


# ===================================================
# AKTUÁLIS ÁRAK + PERFORMANCE
# ===================================================

if not db_poziciok.empty:

    aktualis_arok = (
        arak_lekerese(
            db_poziciok[
                "Ticker"
            ].tolist()
        )
    )


    performance = (
        performance_szamitas_db(
            db_poziciok,
            aktualis_arok
        )
    )


else:

    aktualis_arok = {}


    performance = (
        performance_szamitas_db(
            db_poziciok,
            aktualis_arok
        )
    )


# ===================================================
# PERFORMANCE KPI
# ===================================================

if not performance.empty:

    befektetett = (
        performance[
            "Bekerülési érték"
        ]
        .fillna(0)
        .sum()
    )


    aktualis = (
        performance[
            "Aktuális érték"
        ]
        .fillna(0)
        .sum()
    )


    profit = (
        performance[
            "Profit"
        ]
        .fillna(0)
        .sum()
    )


    realizalt_profit = (
        performance[
            "Realizált P/L"
        ]
        .fillna(0)
        .sum()
    )


else:

    befektetett = 0.0

    aktualis = 0.0

    profit = 0.0

    realizalt_profit = 0.0


if befektetett != 0:

    hozam = (
        profit
        / befektetett
        * 100
    )

else:

    hozam = 0.0


# ===================================================
# RISK SCORE
# ===================================================

if not portfolio.empty:

    try:

        score, szint, uzenetek = (
            risk_score_szamitas(
                portfolio
            )
        )


    except Exception:

        score = 0

        szint = (
            "Nem számítható"
        )

        uzenetek = []


else:

    score = 0


    szint = (
        "Nincs portfólióadat"
    )


    uzenetek = [
        (
            "Adj hozzá legalább egy BUY tranzakciót "
            "a portfólióelemzés elindításához."
        )
    ]


# ===================================================
# MARKET DATA
# ===================================================

try:

    market_adatok = (
        market_overview_lekerese()
    )

except Exception:

    market_adatok = []


# ===================================================
# HISTORY
# ===================================================

if not portfolio.empty:

    try:

        tortenet = (
            portfolio_tortenet(
                portfolio
            )
        )

    except Exception:

        tortenet = (
            pd.DataFrame(
                columns=[
                    "Portfolio"
                ]
            )
        )


    try:

        napi_adatok = (
            portfolio_napi_teljesitmeny(
                portfolio
            )
        )

    except Exception:

        napi_adatok = []


else:

    tortenet = pd.DataFrame(
        columns=[
            "Portfolio"
        ]
    )


    napi_adatok = []


# ===================================================
# RISK BENCHMARK
# ===================================================

if not tortenet.empty:

    try:

        risk_benchmark_adatok = (
            benchmark_osszehasonlitas(
                tortenet,
                "1Y"
            )
        )

    except Exception:

        risk_benchmark_adatok = (
            pd.DataFrame()
        )


else:

    risk_benchmark_adatok = (
        pd.DataFrame()
    )


# ===================================================
# HOLDINGS
# ===================================================

if not portfolio.empty:

    try:

        holdings = (
            holdings_tabla_keszites(
                portfolio,
                performance,
                aktualis_arok,
                napi_adatok,
                teljes_portfolio_ertek
            )
        )

    except Exception:

        holdings = (
            pd.DataFrame()
        )


else:

    holdings = (
        pd.DataFrame()
    )


# ===================================================
# HOLDINGS FORMÁZÁS
# ===================================================

def pnl_szin(
    value
):

    if value is None:

        return ""


    try:

        if value > 0:

            return (
                "color: #059669;"
                "font-weight: 600;"
            )


        if value < 0:

            return (
                "color: #dc2626;"
                "font-weight: 600;"
            )


    except Exception:

        pass


    return ""


def holdings_formazas(
    dataframe
):

    styled = (
        dataframe
        .style
        .format(
            {
                "Quantity":
                    "{:,.4f}",

                "Price":
                    "{:,.2f}",

                "Market Value":
                    "{:,.2f}",

                "Weight %":
                    "{:.2f}%",

                "Cost Basis":
                    "{:,.2f}",

                "P/L":
                    "{:+,.2f}",

                "P/L %":
                    "{:+.2f}%",

                "Daily %":
                    "{:+.2f}%"
            },
            na_rep="—"
        )
    )


    szinezheto = [

        oszlop

        for oszlop
        in [
            "P/L",
            "P/L %",
            "Daily %"
        ]

        if oszlop
        in dataframe.columns
    ]


    if szinezheto:

        styled = (
            styled.map(
                pnl_szin,
                subset=szinezheto
            )
        )


    return styled


# ===================================================
# WATCHLIST
# ===================================================

if (
    "watchlist_tickerek"
    not in st.session_state
):

    st.session_state[
        "watchlist_tickerek"
    ] = [
        "NVDA",
        "AAPL",
        "MSFT",
        "TSLA",
        "AMD",
        "META"
    ]


# ===================================================
# TABOK
# ===================================================

tab0, tab1, tab2, tab3, tab4 = (
    st.tabs(
        [
            "🏠 Kezdőlap",
            "💼 Portfólió",
            "👀 Piac",
            "🔎 Részvényelemzés",
            "🤖 AI Asszisztens"
        ]
    )
)


# ===================================================
# TAB 0
# KEZDŐLAP
# ===================================================

with tab0:

    st.subheader(
        "🏠 Vezetői áttekintés"
    )


    st.caption(
        "A portfólió, a piac és a kockázatok gyors összefoglalója"
    )


    # =================================================
    # ÜRES PORTFÓLIÓ
    # =================================================

    if not van_tranzakcio:

        st.info(
            "Még nincs rögzített tranzakció. "
            "Nyisd meg a 💼 Portfólió fület, majd adj hozzá "
            "egy BUY tranzakciót."
        )


    # =================================================
    # KPI
    # =================================================

    home1, home2, home3, home4 = (
        st.columns(4)
    )


    with home1:

        st.metric(
            "💰 Teljes portfólió",
            f"{teljes_portfolio_ertek:,.0f} Ft"
        )


    with home2:

        st.metric(
            "💵 Készpénz",
            f"{cash_huf:,.0f} Ft",
            f"{cash_szazalek:.1f}%"
        )


    with home3:

        st.metric(
            "📈 Teljes hozam",
            (
                f"{hozam:+.2f}%"
                if not portfolio.empty
                else "—"
            )
        )


    with home4:

        st.metric(
            "🧠 Risk Score",
            (
                f"{score}/100"
                if not portfolio.empty
                else "—"
            )
        )


    st.divider()


    # =================================================
    # TŐKEALLOKÁCIÓ
    # =================================================

    st.subheader(
        "💵 Tőkeallokáció"
    )


    cap1, cap2, cap3, cap4 = (
        st.columns(4)
    )


    with cap1:

        st.metric(
            "Befektetett összeg",
            f"{teljes_ertek:,.0f} Ft"
        )


    with cap2:

        st.metric(
            "Készpénz",
            f"{cash_huf:,.0f} Ft"
        )


    with cap3:

        st.metric(
            "Készpénz arány",
            f"{cash_szazalek:.2f}%"
        )


    with cap4:

        st.metric(
            "Elérhető összeg",
            f"{cash_huf:,.0f} Ft"
        )


    st.divider()


    # =================================================
    # PIACI PILLANATKÉP
    # =================================================

    st.subheader(
        "🌎 Piaci pillanatkép"
    )


    if market_adatok:

        market_cols = (
            st.columns(
                len(
                    market_adatok
                )
            )
        )


        for col, adat in zip(
            market_cols,
            market_adatok
        ):

            with col:

                ertek = adat[
                    "Érték"
                ]


                tipus = adat[
                    "Típus"
                ]


                if tipus == "yield":

                    text = (
                        f"{ertek:.2f}%"
                    )


                elif tipus == "index":

                    text = (
                        f"{ertek:,.2f}"
                    )


                elif adat[
                    "Név"
                ] in [
                    "Bitcoin",
                    "Gold"
                ]:

                    text = (
                        f"${ertek:,.0f}"
                    )


                else:

                    text = (
                        f"{ertek:,.2f}"
                    )


                st.metric(
                    adat[
                        "Név"
                    ],
                    text,
                    f"{adat['Napi változás %']:+.2f}%"
                )


    st.divider()


    # =================================================
    # PORTFÓLIÓ ÁLLAPOT
    # =================================================

    st.subheader(
        "🧠 Portfólió állapot"
    )


    status1, status2, status3, status4 = (
        st.columns(4)
    )


    with status1:

        st.metric(
            "Pozíciók",
            f"{len(portfolio)} db"
        )


    with status2:

        st.metric(
            "Készpénz arány",
            f"{cash_szazalek:.1f}%"
        )


    with status3:

        if legnagyobb is not None:

            st.metric(
                "Legnagyobb pozíció",
                f"{legnagyobb['Súly %']:.1f}%"
            )

        else:

            st.metric(
                "Legnagyobb pozíció",
                "—"
            )


    with status4:

        st.metric(
            "Risk Score",
            (
                f"{score}/100"
                if not portfolio.empty
                else "—"
            )
        )


    # =================================================
    # SZEKTORKITETTSÉG
    # =================================================

    if not sector_exposure.empty:

        st.divider()


        st.subheader(
            "🌍 Valódi szektorkitettség"
        )


        st.caption(
            "ETF look-through alapján számított kitettség"
        )


        top5 = (
            sector_exposure
            .head(5)
        )


        fig_sector_home = (
            px.bar(
                top5,
                x="Súly %",
                y="Sector",
                orientation="h"
            )
        )


        fig_sector_home.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            height=300,
            xaxis_title="Portfólió súly %",
            yaxis_title=""
        )


        st.plotly_chart(
            fig_sector_home,
            width="stretch"
        )


# ===================================================
# TAB 1
# PORTFÓLIÓ
# ===================================================

with tab1:

    st.subheader(
        "💼 Portfólió Áttekintés"
    )


    if van_tranzakcio:

        st.success(
            "Adatforrás: saját SQLite tranzakciós napló"
        )

    else:

        st.info(
            "A portfólió jelenleg üres. "
            "Semmilyen régi vagy tesztportfólió nincs betöltve."
        )


    # =================================================
    # KPI
    # =================================================

    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "💰 Teljes portfólió",
            f"{teljes_portfolio_ertek:,.0f} Ft"
        )


    with col2:

        st.metric(
            "📈 Befektetve",
            f"{teljes_ertek:,.0f} Ft"
        )


    with col3:

        st.metric(
            "💵 Készpénz",
            f"{cash_huf:,.0f} Ft"
        )


    with col4:

        st.metric(
            "Készpénz arány",
            f"{cash_szazalek:.2f}%"
        )


    st.divider()


    # =================================================
    # PORTFÓLIÓ KEZELÉSE
    # =================================================

    st.subheader(
        "⚙️ Portfólió kezelése"
    )


    st.caption(
        "A portfólió kizárólag az itt rögzített BUY és SELL "
        "tranzakciókból épül fel."
    )


    # =================================================
    # ÚJ TRANZAKCIÓ
    # =================================================

    with st.expander(
        "➕ Új tranzakció",
        expanded=not van_tranzakcio
    ):

        with st.form(
            "uj_tranzakcio_form"
        ):

            left, right = (
                st.columns(2)
            )


            with left:

                trade_date = (
                    st.date_input(
                        "Tranzakció dátuma"
                    )
                )


                ticker_input = (
                    st.text_input(
                        "Ticker",
                        placeholder="Pl. AAPL vagy CSPX.L"
                    )
                )


                asset_name_input = (
                    st.text_input(
                        "Eszköz neve",
                        placeholder="Pl. Apple Inc."
                    )
                )


                side_input = (
                    st.selectbox(
                        "Tranzakció típusa",
                        [
                            "BUY",
                            "SELL"
                        ]
                    )
                )


            with right:

                quantity_input = (
                    st.number_input(
                        "Darabszám",
                        min_value=0.000001,
                        value=1.0,
                        step=0.1,
                        format="%.6f"
                    )
                )


                price_input = (
                    st.number_input(
                        "Ár",
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        format="%.4f"
                    )
                )


                currency_input = (
                    st.selectbox(
                        "Deviza",
                        [
                            "USD",
                            "EUR",
                            "GBP",
                            "HUF",
                            "CHF"
                        ]
                    )
                )


                fee_input = (
                    st.number_input(
                        "Tranzakciós díj",
                        min_value=0.0,
                        value=0.0,
                        step=0.1,
                        format="%.4f"
                    )
                )


            note_input = (
                st.text_input(
                    "Megjegyzés",
                    placeholder="Opcionális"
                )
            )


            mentes = (
                st.form_submit_button(
                    "💾 Tranzakció mentése"
                )
            )


        if mentes:

            ticker_clean = (
                ticker_input
                .strip()
                .upper()
            )


            asset_clean = (
                asset_name_input
                .strip()
            )


            if not ticker_clean:

                st.error(
                    "Add meg a tickert."
                )


            elif not asset_clean:

                st.error(
                    "Add meg az eszköz nevét."
                )


            elif price_input <= 0:

                st.error(
                    "Az árnak 0-nál nagyobbnak kell lennie."
                )


            else:

                try:

                    # -----------------------------------
                    # SELL ELŐZETES ELLENŐRZÉS
                    # -----------------------------------

                    if side_input == "SELL":

                        jelenlegi_tx = (
                            tranzakciok_betoltese_db()
                        )


                        jelenlegi_poziciok = (
                            poziciok_szamitas_db(
                                jelenlegi_tx
                            )
                        )


                        talalat = (
                            jelenlegi_poziciok[
                                jelenlegi_poziciok[
                                    "Ticker"
                                ] == ticker_clean
                            ]
                        )


                        if talalat.empty:

                            raise ValueError(
                                f"Nincs aktív {ticker_clean} pozíciód."
                            )


                        elerheto = float(
                            talalat.iloc[
                                0
                            ][
                                "Darab"
                            ]
                        )


                        if (
                            quantity_input
                            > elerheto
                            + 1e-10
                        ):

                            raise ValueError(
                                f"Maximum {elerheto:g} db "
                                f"{ticker_clean} adható el."
                            )


                    tranzakcio_hozzaadas(
                        trade_date=(
                            trade_date.isoformat()
                        ),
                        ticker=(
                            ticker_clean
                        ),
                        asset_name=(
                            asset_clean
                        ),
                        side=(
                            side_input
                        ),
                        quantity=(
                            quantity_input
                        ),
                        price=(
                            price_input
                        ),
                        currency=(
                            currency_input
                        ),
                        fee=(
                            fee_input
                        ),
                        note=(
                            note_input
                        )
                    )


                    # -----------------------------------
                    # UTÓLAGOS VALIDÁLÁS
                    # -----------------------------------

                    uj_tx = (
                        tranzakciok_betoltese_db()
                    )


                    poziciok_szamitas_db(
                        uj_tx
                    )


                    st.success(
                        "Tranzakció sikeresen elmentve."
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        f"A tranzakció nem menthető: {e}"
                    )


    # =================================================
    # TRANZAKCIÓS NAPLÓ
    # =================================================

    with st.expander(
        "📒 Tranzakciós napló",
        expanded=False
    ):

        aktualis_tx = (
            tranzakciok_betoltese_db()
        )


        if aktualis_tx.empty:

            st.info(
                "Még nincs rögzített tranzakció."
            )


        else:

            tabla = (
                aktualis_tx[
                    [
                        "id",
                        "trade_date",
                        "ticker",
                        "asset_name",
                        "side",
                        "quantity",
                        "price",
                        "currency",
                        "fee",
                        "note"
                    ]
                ]
                .copy()
            )


            tabla = (
                tabla.rename(
                    columns={
                        "id":
                            "ID",

                        "trade_date":
                            "Dátum",

                        "ticker":
                            "Ticker",

                        "asset_name":
                            "Eszköz",

                        "side":
                            "Típus",

                        "quantity":
                            "Darabszám",

                        "price":
                            "Ár",

                        "currency":
                            "Deviza",

                        "fee":
                            "Díj",

                        "note":
                            "Megjegyzés"
                    }
                )
            )


            tabla = (
                tabla.sort_values(
                    [
                        "Dátum",
                        "ID"
                    ],
                    ascending=False
                )
            )


            st.dataframe(
                tabla,
                width="stretch",
                hide_index=True
            )


            st.markdown(
                "#### Tranzakció törlése"
            )


            transaction_ids = (
                aktualis_tx[
                    "id"
                ]
                .tolist()
            )


            def transaction_label(
                transaction_id
            ):

                sor = (
                    aktualis_tx[
                        aktualis_tx[
                            "id"
                        ] == transaction_id
                    ]
                    .iloc[0]
                )


                return (
                    f"#{transaction_id} • "
                    f"{sor['trade_date']} • "
                    f"{sor['side']} • "
                    f"{sor['ticker']} • "
                    f"{sor['quantity']:g} db"
                )


            torlendo_id = (
                st.selectbox(
                    "Törlendő tranzakció",
                    transaction_ids,
                    format_func=(
                        transaction_label
                    )
                )
            )


            if st.button(
                "🗑️ Kiválasztott tranzakció törlése"
            ):

                teszt = (
                    aktualis_tx[
                        aktualis_tx[
                            "id"
                        ] != torlendo_id
                    ]
                    .copy()
                )


                try:

                    if not teszt.empty:

                        poziciok_szamitas_db(
                            teszt
                        )


                    tranzakcio_torles(
                        torlendo_id
                    )


                    st.success(
                        "Tranzakció törölve."
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        "A tranzakció nem törölhető, "
                        "mert érvénytelenné tenné a "
                        f"tranzakciós előzményt: {e}"
                    )


    st.divider()


    # =================================================
    # KÉSZPÉNZ
    # =================================================

    st.subheader(
        "💵 Készpénz kezelés"
    )


    cash_left, cash_right = (
        st.columns(
            [
                1,
                2
            ]
        )
    )


    with cash_left:

        uj_cash = (
            st.number_input(
                "Készpénz egyenleg (HUF)",
                min_value=0.0,
                value=float(
                    cash_huf
                ),
                step=10000.0,
                format="%.0f"
            )
        )


        if st.button(
            "💾 Készpénz mentése"
        ):

            cash_mentes_db(
                uj_cash
            )


            st.success(
                "Készpénz egyenleg elmentve."
            )


            st.rerun()


    with cash_right:

        c1, c2, c3 = (
            st.columns(3)
        )


        with c1:

            st.metric(
                "Befektetett összeg",
                f"{teljes_ertek:,.0f} Ft"
            )


        with c2:

            st.metric(
                "Készpénz arány",
                f"{cash_szazalek:.2f}%"
            )


        with c3:

            st.metric(
                "Elérhető összeg",
                f"{cash_huf:,.0f} Ft"
            )


    st.divider()


    # =================================================
    # HOLDINGS
    # =================================================

    st.subheader(
        "📋 Portfólióállomány"
    )


    st.caption(
        "Aktuális pozíciók • súly • bekerülési érték • "
        "P/L • napi teljesítmény"
    )


    if holdings.empty:

        st.info(
            "Nincs aktív pozíció."
        )


    else:

        st.dataframe(
            holdings_formazas(
                holdings
            ),
            width="stretch",
            hide_index=True
        )


    st.caption(
        "A Price, Market Value, Cost Basis és P/L "
        "az instrumentum kereskedési devizájában jelenik meg. "
        "A Weight % HUF-alapú portfólióértékből számolódik."
    )


    # =================================================
    # TOVÁBBI ELEMZÉSEK CSAK AKKOR,
    # HA VAN PORTFÓLIÓ
    # =================================================

    if not portfolio.empty:

        st.divider()


        # =============================================
        # ETF LOOK-THROUGH
        # =============================================

        st.subheader(
            "🌍 ETF szektor megoszlás"
        )


        if sector_exposure.empty:

            st.info(
                "Nincs elérhető szektorkitettségi adat."
            )


        else:

            fig_sector = (
                px.bar(
                    sector_exposure,
                    x="Súly %",
                    y="Sector",
                    orientation="h"
                )
            )


            fig_sector.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                height=420,
                xaxis_title="Portfólió súly %",
                yaxis_title=""
            )


            st.plotly_chart(
                fig_sector,
                width="stretch"
            )


        # =============================================
        # EXPOSURE
        # =============================================

        if (
            not currency_exposure.empty
            or not asset_class_exposure.empty
        ):

            st.divider()


            st.subheader(
                "🧩 További kitettségek"
            )


            e1, e2 = (
                st.columns(2)
            )


            with e1:

                st.markdown(
                    "#### Deviza megoszlás"
                )


                if (
                    not currency_exposure.empty
                    and "HUF érték"
                    in currency_exposure.columns
                    and "Deviza"
                    in currency_exposure.columns
                ):

                    fig_currency = (
                        px.pie(
                            currency_exposure,
                            values="HUF érték",
                            names="Deviza",
                            hole=0.55
                        )
                    )


                    st.plotly_chart(
                        fig_currency,
                        width="stretch"
                    )


            with e2:

                st.markdown(
                    "#### Eszközallokáció"
                )


                if (
                    not asset_class_exposure.empty
                    and "HUF érték"
                    in asset_class_exposure.columns
                    and "Asset Class"
                    in asset_class_exposure.columns
                ):

                    fig_asset = (
                        px.pie(
                            asset_class_exposure,
                            values="HUF érték",
                            names="Asset Class",
                            hole=0.55
                        )
                    )


                    st.plotly_chart(
                        fig_asset,
                        width="stretch"
                    )


        # =============================================
        # BENCHMARK
        # =============================================

        st.divider()


        st.subheader(
            "📈 Portfólió vs Benchmark"
        )


        idotav = (
            st.selectbox(
                "Időtáv",
                [
                    "1M",
                    "3M",
                    "6M",
                    "1Y"
                ],
                index=3
            )
        )


        if not tortenet.empty:

            try:

                benchmark_adatok = (
                    benchmark_osszehasonlitas(
                        tortenet,
                        idotav
                    )
                )


                returns = (
                    benchmark_hozamok(
                        benchmark_adatok
                    )
                )


            except Exception:

                benchmark_adatok = (
                    pd.DataFrame()
                )

                returns = {}


        else:

            benchmark_adatok = (
                pd.DataFrame()
            )

            returns = {}


        b1, b2, b3 = (
            st.columns(3)
        )


        with b1:

            value = returns.get(
                "Portfolio"
            )


            st.metric(
                "Portfólió",
                (
                    f"{value:+.2f}%"
                    if value is not None
                    else "N/A"
                )
            )


        with b2:

            value = returns.get(
                "S&P 500"
            )


            st.metric(
                "S&P 500",
                (
                    f"{value:+.2f}%"
                    if value is not None
                    else "N/A"
                )
            )


        with b3:

            value = returns.get(
                "Nasdaq 100"
            )


            st.metric(
                "Nasdaq 100",
                (
                    f"{value:+.2f}%"
                    if value is not None
                    else "N/A"
                )
            )


        if not benchmark_adatok.empty:

            fig_benchmark = (
                go.Figure()
            )


            for (
                oszlop,
                nev
            ) in [
                (
                    "Portfolio",
                    "Portfólió"
                ),
                (
                    "S&P 500",
                    "S&P 500"
                ),
                (
                    "Nasdaq 100",
                    "Nasdaq 100"
                )
            ]:

                if (
                    oszlop
                    in benchmark_adatok.columns
                ):

                    fig_benchmark.add_trace(
                        go.Scatter(
                            x=(
                                benchmark_adatok.index
                            ),
                            y=(
                                benchmark_adatok[
                                    oszlop
                                ]
                            ),
                            mode="lines",
                            name=nev
                        )
                    )


            fig_benchmark.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                height=370,
                hovermode="x unified"
            )


            st.plotly_chart(
                fig_benchmark,
                width="stretch"
            )


        # =============================================
        # RISK
        # =============================================

        st.divider()


        st.subheader(
            "🧠 Kockázatelemzés"
        )


        st.caption(
            "Volatilitás • Max Drawdown • Sharpe • "
            "Sortino • Beta • Value at Risk"
        )


        rf = (
            st.number_input(
                "Kockázatmentes hozam (%)",
                min_value=0.0,
                max_value=20.0,
                value=0.0,
                step=0.25
            )
        )


        if not tortenet.empty:

            risk = (
                risk_analytics_szamitas(
                    tortenet,
                    risk_benchmark_adatok,
                    teljes_portfolio_ertek,
                    rf
                )
            )


        else:

            risk = {
                "Volatilitás %":
                    None,

                "Max Drawdown %":
                    None,

                "Sharpe Ratio":
                    None,

                "Sortino Ratio":
                    None,

                "Beta":
                    None,

                "VaR 95% %":
                    None,

                "VaR 95% HUF":
                    None
            }


        r1, r2, r3 = (
            st.columns(3)
        )


        with r1:

            value = risk[
                "Volatilitás %"
            ]


            st.metric(
                "Éves volatilitás",
                (
                    f"{value:.2f}%"
                    if value is not None
                    else "N/A"
                )
            )


        with r2:

            value = risk[
                "Max Drawdown %"
            ]


            st.metric(
                "Max Drawdown",
                (
                    f"{value:.2f}%"
                    if value is not None
                    else "N/A"
                )
            )


        with r3:

            value = risk[
                "Beta"
            ]


            st.metric(
                "Beta vs S&P 500",
                (
                    f"{value:.2f}"
                    if value is not None
                    else "N/A"
                )
            )


        r4, r5, r6 = (
            st.columns(3)
        )


        with r4:

            value = risk[
                "Sharpe Ratio"
            ]


            st.metric(
                "Sharpe Ratio",
                (
                    f"{value:.2f}"
                    if value is not None
                    else "N/A"
                )
            )


        with r5:

            value = risk[
                "Sortino Ratio"
            ]


            st.metric(
                "Sortino Ratio",
                (
                    f"{value:.2f}"
                    if value is not None
                    else "N/A"
                )
            )


        with r6:

            var_pct = (
                risk[
                    "VaR 95% %"
                ]
            )


            var_huf = (
                risk[
                    "VaR 95% HUF"
                ]
            )


            if (
                var_pct is not None
                and var_huf is not None
            ):

                st.metric(
                    "1 napos VaR 95%",
                    f"{abs(var_pct):.2f}%",
                    f"{var_huf:,.0f} Ft"
                )

            else:

                st.metric(
                    "1 napos VaR 95%",
                    "N/A"
                )


        # =============================================
        # DRAWDOWN
        # =============================================

        if not tortenet.empty:

            drawdown = (
                drawdown_idosor(
                    tortenet
                )
            )


            if not drawdown.empty:

                st.markdown(
                    "#### 📉 Drawdown"
                )


                fig_drawdown = (
                    go.Figure()
                )


                fig_drawdown.add_trace(
                    go.Scatter(
                        x=(
                            drawdown.index
                        ),
                        y=(
                            drawdown[
                                "Drawdown %"
                            ]
                        ),
                        mode="lines",
                        fill="tozeroy"
                    )
                )


                fig_drawdown.update_layout(
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                    height=300
                )


                st.plotly_chart(
                    fig_drawdown,
                    width="stretch"
                )


        # =============================================
        # RISK SCORE
        # =============================================

        st.markdown(
            "#### 🧠 Portfólió kockázati értékelés"
        )


        rr1, rr2 = (
            st.columns(2)
        )


        with rr1:

            st.metric(
                "Risk Score",
                f"{score}/100"
            )


        with rr2:

            if legnagyobb is not None:

                st.metric(
                    "Legnagyobb súly",
                    f"{legnagyobb['Súly %']:.2f}%"
                )


        st.write(
            szint
        )


        for uzenet in uzenetek:

            st.write(
                uzenet
            )


        # =============================================
        # PERFORMANCE
        # =============================================

        st.divider()


        st.subheader(
            "💹 Portfólió Teljesítmény"
        )


        st.caption(
            "Befektetési teljesítmény áttekintése"
        )


        p1, p2, p3, p4 = (
            st.columns(4)
        )


        with p1:

            st.metric(
                "Befektetett tőke",
                f"{befektetett:,.2f}"
            )


        with p2:

            st.metric(
                "Aktuális érték",
                f"{aktualis:,.2f}"
            )


        with p3:

            st.metric(
                "Nem realizált P/L",
                f"{profit:+,.2f}"
            )


        with p4:

            st.metric(
                "Teljes hozam",
                f"{hozam:+.2f}%"
            )


        st.metric(
            "Realizált P/L",
            f"{realizalt_profit:+,.2f}"
        )


# ===================================================
# TAB 2
# PIAC
# ===================================================

with tab2:

    st.subheader(
        "🌎 Piaci áttekintés"
    )


    st.caption(
        "Részvények • Volatilitás • Kamatok • Nyersanyagok • Kripto"
    )


    if market_adatok:

        market_cols = (
            st.columns(
                len(
                    market_adatok
                )
            )
        )


        for col, adat in zip(
            market_cols,
            market_adatok
        ):

            with col:

                st.metric(
                    adat[
                        "Név"
                    ],
                    f"{adat['Érték']:,.2f}",
                    f"{adat['Napi változás %']:+.2f}%"
                )


    st.divider()


    st.subheader(
        "👀 Market Watchlist"
    )


    with st.expander(
        "⚙️ Watchlist kezelése"
    ):

        uj_ticker = (
            st.text_input(
                "Új ticker hozzáadása",
                placeholder="Pl. GOOGL"
            )
        )


        add_col, remove_col = (
            st.columns(2)
        )


        with add_col:

            if st.button(
                "➕ Hozzáadás"
            ):

                ticker = (
                    uj_ticker
                    .strip()
                    .upper()
                )


                if (
                    ticker
                    and ticker
                    not in st.session_state[
                        "watchlist_tickerek"
                    ]
                ):

                    st.session_state[
                        "watchlist_tickerek"
                    ].append(
                        ticker
                    )


                    st.rerun()


        with remove_col:

            if st.session_state[
                "watchlist_tickerek"
            ]:

                torlendo = (
                    st.selectbox(
                        "Eltávolítandó ticker",
                        st.session_state[
                            "watchlist_tickerek"
                        ]
                    )
                )


                if st.button(
                    "🗑️ Eltávolítás"
                ):

                    st.session_state[
                        "watchlist_tickerek"
                    ].remove(
                        torlendo
                    )


                    st.rerun()


    try:

        watchlist = (
            watchlist_lekerese(
                st.session_state[
                    "watchlist_tickerek"
                ]
            )
        )

    except Exception:

        watchlist = []


    if watchlist:

        cols = (
            st.columns(
                len(
                    watchlist
                )
            )
        )


        for col, adat in zip(
            cols,
            watchlist
        ):

            with col:

                st.metric(
                    adat[
                        "Ticker"
                    ],
                    f"${adat['Ár']:.2f}",
                    f"{adat['Napi változás %']:+.2f}%"
                )


        st.divider()


        st.subheader(
            "📈 Price Chart"
        )


        tickerek = [

            adat[
                "Ticker"
            ]

            for adat
            in watchlist
        ]


        selected = (
            st.selectbox(
                "Válassz egy részvényt:",
                tickerek
            )
        )


        st.session_state[
            "kivalasztott_ticker"
        ] = selected


        try:

            history = (
                watchlist_tortenet(
                    selected
                )
            )


            fig = (
                px.line(
                    history,
                    x="Dátum",
                    y="Ár",
                    title=(
                        f"{selected} - "
                        f"30 napos árfolyam"
                    )
                )
            )


            st.plotly_chart(
                fig,
                width="stretch"
            )


        except Exception as e:

            st.warning(
                f"Az árfolyamgrafikon nem tölthető be: {e}"
            )


# ===================================================
# TAB 3
# RÉSZVÉNYELEMZÉS
# ===================================================

with tab3:

    st.subheader(
        "🔎 Equity Research"
    )


    elemzett_ticker = (
        st.session_state.get(
            "kivalasztott_ticker",
            "AAPL"
        )
    )


    try:

        snapshot = (
            stock_snapshot(
                elemzett_ticker
            )
        )


        st.markdown(
            f"## {snapshot['Név']}"
        )


        st.caption(
            snapshot[
                "Ticker"
            ]
        )


        st.markdown(
            "### Market Overview"
        )


        s1, s2, s3, s4 = (
            st.columns(4)
        )


        with s1:

            st.metric(
                "Aktuális ár",
                f"${snapshot['Ár']:.2f}",
                f"{snapshot['Napi változás %']:+.2f}%"
            )


        with s2:

            market_cap = (
                snapshot[
                    "Market Cap"
                ]
            )


            if market_cap:

                if (
                    market_cap
                    >= 1_000_000_000_000
                ):

                    cap_text = (
                        f"${market_cap / 1_000_000_000_000:.2f}T"
                    )

                else:

                    cap_text = (
                        f"${market_cap / 1_000_000_000:.2f}B"
                    )

            else:

                cap_text = "N/A"


            st.metric(
                "Market Cap",
                cap_text
            )


        with s3:

            return_30d = (
                snapshot[
                    "30D hozam %"
                ]
            )


            st.metric(
                "30D Return",
                (
                    f"{return_30d:.2f}%"
                    if return_30d is not None
                    else "N/A"
                )
            )


        with s4:

            st.metric(
                "Valuation",
                snapshot[
                    "Valuation Status"
                ]
            )


        st.divider()


        st.markdown(
            "### 📊 Valuation"
        )


        valuation = [
            (
                "P/E",
                "P/E"
            ),
            (
                "Forward P/E",
                "Forward P/E"
            ),
            (
                "P/S",
                "P/S"
            ),
            (
                "EV/EBITDA",
                "EV/EBITDA"
            )
        ]


        valuation_cols = (
            st.columns(4)
        )


        for col, (
            label,
            key
        ) in zip(
            valuation_cols,
            valuation
        ):

            with col:

                value = (
                    snapshot[
                        key
                    ]
                )


                st.metric(
                    label,
                    (
                        f"{value:.2f}x"
                        if value is not None
                        else "N/A"
                    )
                )


        st.divider()


        st.markdown(
            "### 📈 Price Range"
        )


        q1, q2 = (
            st.columns(2)
        )


        with q1:

            value = (
                snapshot[
                    "52W High"
                ]
            )


            st.metric(
                "52W High",
                (
                    f"${value:.2f}"
                    if value is not None
                    else "N/A"
                )
            )


        with q2:

            value = (
                snapshot[
                    "52W Low"
                ]
            )


            st.metric(
                "52W Low",
                (
                    f"${value:.2f}"
                    if value is not None
                    else "N/A"
                )
            )


    except Exception as e:

        st.error(
            f"A részvényelemzés nem tölthető be: {e}"
        )


# ===================================================
# TAB 4
# AI ASSZISZTENS
# ===================================================

with tab4:

    st.subheader(
        "🤖 AI Portfolio Analyst"
    )


    if (
        portfolio.empty
        or performance.empty
    ):

        st.info(
            "Még nincs elemezhető portfólió. "
            "Adj hozzá legalább egy BUY tranzakciót "
            "a 💼 Portfólió fülön."
        )


    else:

        try:

            ai_elemzes = (
                portfolio_ai_elemzes(
                    portfolio,
                    performance,
                    score
                )
            )


            for uzenet in ai_elemzes:

                st.write(
                    uzenet
                )


        except Exception as e:

            st.error(
                f"Az AI Portfolio Analyst hibát jelzett: {e}"
            )