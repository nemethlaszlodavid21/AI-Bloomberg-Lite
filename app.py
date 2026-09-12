import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from portfolio_import import portfolio_betoltes
from portfolio_analysis import portfolio_elemzes
from portfolio_value import portfolio_ertek_szamitas
from portfolio_performance import portfolio_napi_teljesitmeny
from portfolio_risk import risk_score_szamitas
from portfolio_history import portfolio_tortenet

from portfolio_benchmark import (
    benchmark_osszehasonlitas,
    benchmark_hozamok
)

from portfolio_transactions import (
    tranzakciok_betoltese
)

from portfolio_positions import (
    pozicio_osszesites
)

from portfolio_performance_engine import (
    teljesitmeny_szamitas
)

from portfolio_exposure import (
    portfolio_exposure_szamitas
)

from portfolio_holdings import (
    holdings_tabla_keszites
)

from cash_management import (
    cash_betoltes,
    cash_mentes,
    cash_mutatok
)

from etf_lookthrough import (
    portfolio_lookthrough
)

from market_data import arak_lekerese
from market_overview import market_overview_lekerese
from ai_analyst import portfolio_ai_elemzes
from watchlist import watchlist_lekerese
from watchlist_history import watchlist_tortenet
from stock_snapshot import stock_snapshot
from style import alkalmaz_style


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
# HEADER
# ===================================================

st.title(
    "AI Bloomberg Lite"
)

st.caption(
    "Portfólióelemzés • Piaci információk • Részvényelemzés"
)


# ===================================================
# PORTFÓLIÓ
# ===================================================

portfolio = portfolio_betoltes()

portfolio = portfolio_ertek_szamitas(
    portfolio
)

portfolio, teljes_ertek = portfolio_elemzes(
    portfolio
)

legnagyobb = portfolio.loc[
    portfolio["Súly %"].idxmax()
]


# ===================================================
# CASH
# ===================================================

cash_huf = cash_betoltes()

cash_adatok = cash_mutatok(
    teljes_ertek,
    cash_huf
)

teljes_portfolio_ertek = cash_adatok[
    "Teljes portfólió"
]


# ===================================================
# PORTFÓLIÓ KITETTSÉG
# ===================================================

(
    _,
    currency_exposure,
    asset_class_exposure
) = portfolio_exposure_szamitas(
    portfolio
)


# ===================================================
# VALÓDI ETF LOOK-THROUGH
# ===================================================

sector_exposure = portfolio_lookthrough(
    portfolio
)


# ===================================================
# TRANZAKCIÓK / PERFORMANCE
# ===================================================

tranzakciok = tranzakciok_betoltese()

poziciok = pozicio_osszesites(
    tranzakciok
)

aktualis_arok = arak_lekerese(
    poziciok["Ticker"].tolist()
)

performance = teljesitmeny_szamitas(
    poziciok,
    aktualis_arok
)

befektetett = performance[
    "Bekerülési érték"
].sum()

aktualis = performance[
    "Aktuális érték"
].sum()

profit = performance[
    "Profit"
].sum()

hozam = (
    profit
    / befektetett
    * 100
    if befektetett != 0
    else 0
)


# ===================================================
# PERFORMANCE DISPLAY
# ===================================================

performance_display = performance.copy()

penz_oszlopok = [
    "Bekerülési érték",
    "Aktuális érték",
    "Profit"
]

for oszlop in penz_oszlopok:

    if oszlop in performance_display.columns:

        performance_display[
            oszlop
        ] = performance_display[
            oszlop
        ].apply(
            lambda x:
                f"{x:,.2f}"
        )


# ===================================================
# RISK SCORE
# ===================================================

score, szint, uzenetek = (
    risk_score_szamitas(
        portfolio
    )
)


# ===================================================
# KÖZÖS ADATOK
# ===================================================

market_adatok = (
    market_overview_lekerese()
)

tortenet = portfolio_tortenet(
    portfolio
)

napi_adatok = (
    portfolio_napi_teljesitmeny(
        portfolio
    )
)


# ===================================================
# PROFESSZIONÁLIS HOLDINGS TÁBLA
# ===================================================

holdings = holdings_tabla_keszites(
    portfolio,
    performance,
    aktualis_arok,
    napi_adatok,
    teljes_portfolio_ertek
)


# ===================================================
# HOLDINGS FORMÁZÁS
# ===================================================

def pnl_szin(value):

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


    styled = styled.map(
        pnl_szin,
        subset=[
            "P/L",
            "P/L %",
            "Daily %"
        ]
    )


    return styled


# ===================================================
# WATCHLIST
# ===================================================

if "watchlist_tickerek" not in (
    st.session_state
):

    st.session_state.watchlist_tickerek = [
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
# TAB 0 — KEZDŐLAP
# ===================================================

with tab0:

    st.subheader(
        "🏠 Vezetői áttekintés"
    )

    st.caption(
        "A portfólió, a piac és a kockázatok gyors összefoglalója"
    )


    # -----------------------------------------------
    # TOP KPI
    # -----------------------------------------------

    home1, home2, home3, home4 = (
        st.columns(4)
    )


    with home1:

        st.metric(
            "💰 Teljes portfólió",
            f"{teljes_portfolio_ertek / 1_000_000:.2f} M Ft"
        )


    with home2:

        st.metric(
            "💵 Cash",
            f"{cash_huf:,.0f} Ft",
            f"{cash_adatok['Cash %']:.1f}%"
        )


    with home3:

        st.metric(
            "📈 Teljes hozam",
            f"{hozam:+.2f}%"
        )


    with home4:

        st.metric(
            "🧠 Risk Score",
            f"{score}/100"
        )


    st.divider()


    # -----------------------------------------------
    # CASH / CAPITAL
    # -----------------------------------------------

    st.subheader(
        "💵 Tőkeallokáció"
    )


    cap1, cap2, cap3, cap4 = (
        st.columns(4)
    )


    with cap1:

        st.metric(
            "Invested Capital",
            f"{teljes_ertek:,.0f} Ft"
        )


    with cap2:

        st.metric(
            "Cash",
            f"{cash_huf:,.0f} Ft"
        )


    with cap3:

        st.metric(
            "Cash %",
            f"{cash_adatok['Cash %']:.2f}%"
        )


    with cap4:

        st.metric(
            "Available Capital",
            f"{cash_adatok['Available capital']:,.0f} Ft"
        )


    st.divider()


    # -----------------------------------------------
    # PIACI PILLANATKÉP
    # -----------------------------------------------

    st.subheader(
        "🌎 Piaci pillanatkép"
    )


    if market_adatok:

        market_home_cols = st.columns(
            len(market_adatok)
        )


        for col, adat in zip(
            market_home_cols,
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

                    megjelenitett_ertek = (
                        f"{ertek:.2f}%"
                    )


                elif tipus == "vix":

                    megjelenitett_ertek = (
                        f"{ertek:.2f}"
                    )


                elif tipus == "index":

                    megjelenitett_ertek = (
                        f"{ertek:,.2f} pts"
                    )


                elif adat["Név"] == "Bitcoin":

                    megjelenitett_ertek = (
                        f"${ertek:,.0f}"
                    )


                elif adat["Név"] == "Gold":

                    megjelenitett_ertek = (
                        f"${ertek:,.0f}"
                    )


                else:

                    megjelenitett_ertek = (
                        f"{ertek:,.2f}"
                    )


                st.metric(
                    adat["Név"],
                    megjelenitett_ertek,
                    (
                        f"{adat['Napi változás %']:+.2f}%"
                    )
                )


    st.divider()


    # -----------------------------------------------
    # BENCHMARK + STATUS
    # -----------------------------------------------

    dashboard_left, dashboard_right = (
        st.columns(
            [2, 1]
        )
    )


    with dashboard_left:

        st.subheader(
            "📈 3 havi teljesítmény"
        )

        st.caption(
            "Portfólió vs S&P 500 vs Nasdaq 100 • HUF • Kezd = 100"
        )


        home_benchmark = (
            benchmark_osszehasonlitas(
                tortenet,
                "3M"
            )
        )


        home_returns = benchmark_hozamok(
            home_benchmark
        )


        if not home_benchmark.empty:

            fig_home = go.Figure()


            if (
                "Portfolio"
                in home_benchmark.columns
            ):

                fig_home.add_trace(
                    go.Scatter(
                        x=home_benchmark.index,
                        y=home_benchmark[
                            "Portfolio"
                        ],
                        mode="lines",
                        name="Portfólió",
                        line=dict(
                            width=3.5,
                            color="#2563eb"
                        )
                    )
                )


            if (
                "S&P 500"
                in home_benchmark.columns
            ):

                fig_home.add_trace(
                    go.Scatter(
                        x=home_benchmark.index,
                        y=home_benchmark[
                            "S&P 500"
                        ],
                        mode="lines",
                        name="S&P 500",
                        line=dict(
                            width=2,
                            color="#6b7280"
                        )
                    )
                )


            if (
                "Nasdaq 100"
                in home_benchmark.columns
            ):

                fig_home.add_trace(
                    go.Scatter(
                        x=home_benchmark.index,
                        y=home_benchmark[
                            "Nasdaq 100"
                        ],
                        mode="lines",
                        name="Nasdaq 100",
                        line=dict(
                            width=2,
                            color="#14b8a6"
                        )
                    )
                )


            fig_home.add_hline(
                y=100,
                line_width=1,
                line_dash="dot",
                line_color="#9ca3af"
            )


            fig_home.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                font=dict(
                    color="#374151"
                ),
                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10
                ),
                height=330,
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0
                ),
                xaxis=dict(
                    showgrid=False
                ),
                yaxis=dict(
                    gridcolor="#f0f2f5"
                )
            )


            st.plotly_chart(
                fig_home,
                width="stretch"
            )


            r1, r2, r3 = st.columns(
                3
            )


            with r1:

                value = (
                    home_returns.get(
                        "Portfolio"
                    )
                )

                st.metric(
                    "Portfólió",
                    (
                        f"{value:+.2f}%"
                        if value is not None
                        else "N/A"
                    )
                )


            with r2:

                value = (
                    home_returns.get(
                        "S&P 500"
                    )
                )

                st.metric(
                    "S&P 500",
                    (
                        f"{value:+.2f}%"
                        if value is not None
                        else "N/A"
                    )
                )


            with r3:

                value = (
                    home_returns.get(
                        "Nasdaq 100"
                    )
                )

                st.metric(
                    "Nasdaq 100",
                    (
                        f"{value:+.2f}%"
                        if value is not None
                        else "N/A"
                    )
                )


    with dashboard_right:

        st.subheader(
            "🧠 Portfólió állapot"
        )


        st.metric(
            "Pozíciók",
            f"{len(portfolio)} db"
        )


        st.metric(
            "Cash arány",
            f"{cash_adatok['Cash %']:.1f}%"
        )


        st.metric(
            "Legnagyobb pozíció",
            f"{legnagyobb['Súly %']:.1f}%"
        )


        st.metric(
            "Risk Score",
            f"{score}/100"
        )


        st.markdown(
            "#### Értékelés"
        )

        st.write(
            szint
        )


    st.divider()


    # -----------------------------------------------
    # LOOK THROUGH SUMMARY
    # -----------------------------------------------

    st.subheader(
        "🌍 Valódi szektorkitettség"
    )

    st.caption(
        "ETF look-through alapján számított kitettség"
    )


    if not sector_exposure.empty:

        top_sector = (
            sector_exposure.iloc[0]
        )


        sector1, sector2 = (
            st.columns(
                [1, 2]
            )
        )


        with sector1:

            st.metric(
                "Legnagyobb szektor",
                top_sector["Sector"],
                (
                    f"{top_sector['Súly %']:.1f}%"
                )
            )


        with sector2:

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
                height=280,
                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10
                ),
                xaxis_title="Portfólió súly %",
                yaxis_title=""
            )

            st.plotly_chart(
                fig_sector_home,
                width="stretch"
            )


# ===================================================
# TAB 1 — PORTFÓLIÓ
# ===================================================

with tab1:

    st.subheader(
        "💼 Portfólió Áttekintés"
    )


    # -----------------------------------------------
    # TOP KPI
    # -----------------------------------------------

    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "💰 Teljes portfólió",
            f"{teljes_portfolio_ertek / 1_000_000:.2f} M Ft"
        )


    with col2:

        st.metric(
            "📈 Befektetve",
            f"{teljes_ertek / 1_000_000:.2f} M Ft"
        )


    with col3:

        st.metric(
            "💵 Készpénz",
            f"{cash_huf:,.0f} Ft"
        )


    with col4:

        st.metric(
            "Cash %",
            f"{cash_adatok['Cash %']:.2f}%"
        )


    st.divider()


    # =================================================
    # KÉSZPÉNZ KEZELÉS
    # =================================================

    st.subheader(
        "💵 Készpénz kezelés"
    )


    cash_left, cash_right = (
        st.columns(
            [1, 2]
        )
    )


    with cash_left:

        uj_cash = st.number_input(
            "Cash egyenleg (HUF)",
            min_value=0.0,
            value=float(
                cash_huf
            ),
            step=10000.0,
            format="%.0f"
        )


        if st.button(
            "💾 Készpénz mentése"
        ):

            cash_mentes(
                uj_cash
            )

            st.success(
                "Készpénz egyenleg elmentve."
            )

            st.rerun()


    with cash_right:

        cash1, cash2, cash3 = (
            st.columns(3)
        )


        with cash1:

            st.metric(
                "Befektetett összeg",
                f"{teljes_ertek:,.0f} Ft"
            )


        with cash2:

            st.metric(
                "Cash %",
                f"{cash_adatok['Cash %']:.2f}%"
            )


        with cash3:

            st.metric(
                "Elérhető összeg",
                f"{cash_adatok['Available capital']:,.0f} Ft"
            )


    st.divider()


    # =================================================
    # PROFESSZIONÁLIS HOLDINGS
    # =================================================

    st.subheader(
        "📋 Portfólióállomány"
    )

    st.caption(
        "Aktuális pozíciók • súly • bekerülési érték • P/L • napi teljesítmény"
    )


    st.dataframe(
        holdings_formazas(
            holdings
        ),
        width="stretch",
        hide_index=True
    )


    st.caption(
        "Megjegyzés: a Price, Market Value, Cost Basis és P/L "
        "az adott instrumentum kereskedési devizájában jelenik meg. "
        "A Weight % számítása HUF-alapú portfólióértékkel történik."
    )


    st.divider()


    # =================================================
    # VALÓDI ETF LOOK-THROUGH
    # =================================================

    st.subheader(
        "🌍 ETF szektor megoszlás"
    )

    st.caption(
        "Az ETF-ek belső szektorösszetételének portfóliósúlyozott elemzése"
    )


    if not sector_exposure.empty:

        sector_left, sector_right = (
            st.columns(
                [1.2, 1]
            )
        )


        with sector_left:

            fig_sector = px.bar(
                sector_exposure,
                x="Súly %",
                y="Sector",
                orientation="h"
            )

            fig_sector.update_layout(
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                height=430,
                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10
                ),
                xaxis_title="Portfólió súly %",
                yaxis_title=""
            )

            fig_sector.update_yaxes(
                categoryorder="total ascending"
            )

            st.plotly_chart(
                fig_sector,
                width="stretch"
            )


        with sector_right:

            sector_display = (
                sector_exposure[
                    [
                        "Sector",
                        "Súly %"
                    ]
                ]
                .copy()
            )


            sector_display[
                "Súly %"
            ] = sector_display[
                "Súly %"
            ].map(
                lambda x:
                    f"{x:.2f}%"
            )


            st.dataframe(
                sector_display,
                width="stretch",
                hide_index=True
            )


            if (
                "Nem besorolt"
                in sector_exposure[
                    "Sector"
                ].values
            ):

                st.warning(
                    "Egy vagy több instrumentumhoz a Yahoo Finance "
                    "nem adott szektoradatot."
                )


    else:

        st.warning(
            "Nem érhető el look-through adat."
        )


    st.divider()


    # =================================================
    # DEVIZA + ASSET CLASS
    # =================================================

    st.subheader(
        "🧩 További kitettségek"
    )


    exp1, exp2 = st.columns(
        2
    )


    with exp1:

        st.markdown(
            "#### Deviza megoszlás"
        )

        fig_currency = px.pie(
            currency_exposure,
            values="HUF érték",
            names="Deviza",
            hole=0.55
        )

        fig_currency.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff"
        )

        st.plotly_chart(
            fig_currency,
            width="stretch"
        )


    with exp2:

        st.markdown(
            "#### Eszközallokáció"
        )

        fig_asset = px.pie(
            asset_class_exposure,
            values="HUF érték",
            names="Asset Class",
            hole=0.55
        )

        fig_asset.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff"
        )

        st.plotly_chart(
            fig_asset,
            width="stretch"
        )


    st.divider()


    # =================================================
    # BENCHMARK
    # =================================================

    st.subheader(
        "📈 Portfólió vs Benchmark"
    )


    bench_header1, bench_header2 = (
        st.columns(
            [3, 1]
        )
    )


    with bench_header1:

        st.caption(
            "Normalizált teljesítmény • HUF • Kezd = 100"
        )


    with bench_header2:

        idotav = st.selectbox(
            "Időtáv",
            [
                "1M",
                "3M",
                "6M",
                "1Y"
            ],
            index=3,
            label_visibility="collapsed"
        )


    benchmark_adatok = (
        benchmark_osszehasonlitas(
            tortenet,
            idotav
        )
    )


    benchmark_returns = (
        benchmark_hozamok(
            benchmark_adatok
        )
    )


    portfolio_return = (
        benchmark_returns.get(
            "Portfolio"
        )
    )

    sp500_return = (
        benchmark_returns.get(
            "S&P 500"
        )
    )

    nasdaq_return = (
        benchmark_returns.get(
            "Nasdaq 100"
        )
    )


    bench1, bench2, bench3 = (
        st.columns(3)
    )


    with bench1:

        st.metric(
            "Portfólió",
            (
                f"{portfolio_return:+.2f}%"
                if portfolio_return is not None
                else "N/A"
            )
        )


    with bench2:

        st.metric(
            "S&P 500",
            (
                f"{sp500_return:+.2f}%"
                if sp500_return is not None
                else "N/A"
            )
        )


    with bench3:

        st.metric(
            "Nasdaq 100",
            (
                f"{nasdaq_return:+.2f}%"
                if nasdaq_return is not None
                else "N/A"
            )
        )


    if not benchmark_adatok.empty:

        fig_benchmark = (
            go.Figure()
        )


        for oszlop, nev, szin, width in [
            (
                "Portfolio",
                "Portfólió",
                "#2563eb",
                3.5
            ),
            (
                "S&P 500",
                "S&P 500",
                "#6b7280",
                2
            ),
            (
                "Nasdaq 100",
                "Nasdaq 100",
                "#14b8a6",
                2
            )
        ]:

            if (
                oszlop
                in benchmark_adatok.columns
            ):

                fig_benchmark.add_trace(
                    go.Scatter(
                        x=benchmark_adatok.index,
                        y=benchmark_adatok[
                            oszlop
                        ],
                        mode="lines",
                        name=nev,
                        line=dict(
                            width=width,
                            color=szin
                        )
                    )
                )


        fig_benchmark.add_hline(
            y=100,
            line_width=1,
            line_dash="dot",
            line_color="#9ca3af"
        )


        fig_benchmark.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            height=370,
            hovermode="x unified",
            margin=dict(
                l=10,
                r=10,
                t=15,
                b=10
            ),
            legend=dict(
                orientation="h"
            ),
            yaxis=dict(
                gridcolor="#f0f2f5"
            )
        )


        st.plotly_chart(
            fig_benchmark,
            width="stretch"
        )


    st.divider()


    # =================================================
    # RISK
    # =================================================

    st.subheader(
        "🧠 Kockázat Áttekintés"
    )


    risk1, risk2 = st.columns(
        2
    )


    with risk1:

        st.metric(
            "Risk Score",
            f"{score}/100"
        )


    with risk2:

        st.metric(
            "Legnagyobb súly",
            f"{legnagyobb['Súly %']:.2f}%"
        )


    st.write(
        szint
    )


    for u in uzenetek:

        st.write(
            u
        )


    st.divider()


    # =================================================
    # PERFORMANCE
    # =================================================

    st.subheader(
        "💹 Portfólió Teljesítmény"
    )

    st.caption(
        "Befektetési teljesítmény áttekintése"
    )


    perf1, perf2, perf3, perf4 = (
        st.columns(4)
    )


    with perf1:

        st.metric(
            "Befektetett tőke",
            f"{befektetett:,.2f}"
        )


    with perf2:

        st.metric(
            "Aktuális érték",
            f"{aktualis:,.2f}"
        )


    with perf3:

        st.metric(
            "P/L",
            f"{profit:+,.2f}"
        )


    with perf4:

        st.metric(
            "Teljes hozam",
            f"{hozam:+.2f}%"
        )


# ===================================================
# TAB 2 — PIAC
# ===================================================

with tab2:

    st.subheader(
        "🌎 Piaci áttekintés"
    )

    st.caption(
        "Részvények • Volatilitás • Kamatok • Nyersanyagok • Kripto"
    )


    if market_adatok:

        market_cols = st.columns(
            len(market_adatok)
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

                    value_text = (
                        f"{ertek:.2f}%"
                    )

                elif tipus == "vix":

                    value_text = (
                        f"{ertek:.2f}"
                    )

                elif tipus == "index":

                    value_text = (
                        f"{ertek:,.2f} pts"
                    )

                elif adat["Név"] in [
                    "Bitcoin",
                    "Gold"
                ]:

                    value_text = (
                        f"${ertek:,.0f}"
                    )

                else:

                    value_text = (
                        f"{ertek:,.2f}"
                    )


                st.metric(
                    adat["Név"],
                    value_text,
                    (
                        f"{adat['Napi változás %']:+.2f}%"
                    )
                )


    st.divider()


    # -----------------------------------------------
    # WATCHLIST
    # -----------------------------------------------

    st.subheader(
        "👀 Market Watchlist"
    )


    with st.expander(
        "⚙️ Watchlist kezelése"
    ):

        uj_ticker = st.text_input(
            "Új ticker hozzáadása",
            placeholder="Pl. GOOGL"
        )


        col_add, col_remove = (
            st.columns(2)
        )


        with col_add:

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
                    not in st.session_state.watchlist_tickerek
                ):

                    st.session_state.watchlist_tickerek.append(
                        ticker
                    )

                    st.rerun()


        with col_remove:

            if (
                st.session_state.watchlist_tickerek
            ):

                eltavolitando = (
                    st.selectbox(
                        "Eltávolítandó ticker",
                        st.session_state.watchlist_tickerek
                    )
                )


                if st.button(
                    "🗑️ Eltávolítás"
                ):

                    st.session_state.watchlist_tickerek.remove(
                        eltavolitando
                    )

                    st.rerun()


    watchlist = watchlist_lekerese(
        st.session_state.watchlist_tickerek
    )


    if watchlist:

        oszlopok = st.columns(
            len(watchlist)
        )


        for oszlop, adat in zip(
            oszlopok,
            watchlist
        ):

            with oszlop:

                st.metric(
                    adat["Ticker"],
                    f"${adat['Ár']:.2f}",
                    (
                        f"{adat['Napi változás %']:+.2f}%"
                    )
                )


    st.divider()


    st.subheader(
        "📈 Price Chart"
    )


    tickerek = [
        adat["Ticker"]
        for adat in watchlist
    ]


    if tickerek:

        kivalasztott_ticker = (
            st.selectbox(
                "Válassz egy részvényt:",
                tickerek
            )
        )


        st.session_state[
            "kivalasztott_ticker"
        ] = kivalasztott_ticker


        torteneti_adatok = (
            watchlist_tortenet(
                kivalasztott_ticker
            )
        )


        fig_watchlist = px.line(
            torteneti_adatok,
            x="Dátum",
            y="Ár",
            title=(
                f"{kivalasztott_ticker} "
                "- 30 napos árfolyam"
            )
        )


        fig_watchlist.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#1f2937",
            xaxis=dict(
                showgrid=False
            ),
            yaxis=dict(
                gridcolor="#e5e7eb"
            )
        )


        st.plotly_chart(
            fig_watchlist,
            width="stretch"
        )


# ===================================================
# TAB 3 — RÉSZVÉNYELEMZÉS
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


    snapshot = stock_snapshot(
        elemzett_ticker
    )


    st.markdown(
        f"## {snapshot['Név']}"
    )

    st.caption(
        snapshot["Ticker"]
    )


    st.markdown(
        "### Market Overview"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    with col1:

        st.metric(
            "Aktuális ár",
            f"${snapshot['Ár']:.2f}",
            (
                f"{snapshot['Napi változás %']:+.2f}%"
            )
        )


    with col2:

        market_cap = snapshot[
            "Market Cap"
        ]


        if market_cap:

            if (
                market_cap
                >= 1_000_000_000_000
            ):

                market_cap_text = (
                    f"${market_cap / 1_000_000_000_000:.2f}T"
                )

            else:

                market_cap_text = (
                    f"${market_cap / 1_000_000_000:.2f}B"
                )

        else:

            market_cap_text = "N/A"


        st.metric(
            "Market Cap",
            market_cap_text
        )


    with col3:

        hozam_30d = snapshot[
            "30D hozam %"
        ]

        st.metric(
            "30D Return",
            (
                f"{hozam_30d:.2f}%"
                if hozam_30d is not None
                else "N/A"
            )
        )


    with col4:

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


    valuation_mezok = [
        (
            "P/E",
            "P/E",
            "x"
        ),
        (
            "Forward P/E",
            "Forward P/E",
            "x"
        ),
        (
            "P/S",
            "P/S",
            "x"
        ),
        (
            "EV/EBITDA",
            "EV/EBITDA",
            "x"
        )
    ]


    valuation_cols = st.columns(
        4
    )


    for col, (
        label,
        key,
        suffix
    ) in zip(
        valuation_cols,
        valuation_mezok
    ):

        with col:

            value = snapshot[
                key
            ]

            st.metric(
                label,
                (
                    f"{value:.2f}{suffix}"
                    if value is not None
                    else "N/A"
                )
            )


    val5, val6, val7 = (
        st.columns(3)
    )


    with val5:

        pb = snapshot["P/B"]

        st.metric(
            "P/B",
            (
                f"{pb:.2f}x"
                if pb is not None
                else "N/A"
            )
        )


    with val6:

        eps = snapshot["EPS"]

        st.metric(
            "EPS",
            (
                f"${eps:.2f}"
                if eps is not None
                else "N/A"
            )
        )


    with val7:

        dividend = snapshot[
            "Dividend Yield %"
        ]

        st.metric(
            "Dividend Yield",
            (
                f"{dividend:.2f}%"
                if dividend is not None
                else "N/A"
            )
        )


    st.divider()


    st.markdown(
        "### 📈 Price Range"
    )


    range1, range2 = (
        st.columns(2)
    )


    with range1:

        high_52w = snapshot[
            "52W High"
        ]

        st.metric(
            "52W High",
            (
                f"${high_52w:.2f}"
                if high_52w is not None
                else "N/A"
            )
        )


    with range2:

        low_52w = snapshot[
            "52W Low"
        ]

        st.metric(
            "52W Low",
            (
                f"${low_52w:.2f}"
                if low_52w is not None
                else "N/A"
            )
        )


# ===================================================
# TAB 4 — AI ASSZISZTENS
# ===================================================

with tab4:

    st.subheader(
        "🤖 AI Portfolio Analyst"
    )


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