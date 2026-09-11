import streamlit as st
import plotly.express as px

from portfolio_import import portfolio_betoltes
from portfolio_analysis import portfolio_elemzes
from portfolio_value import portfolio_ertek_szamitas
from portfolio_performance import portfolio_napi_teljesitmeny
from portfolio_risk import risk_score_szamitas
from portfolio_history import portfolio_tortenet
from portfolio_transactions import tranzakciok_betoltese
from portfolio_positions import pozicio_osszesites
from portfolio_performance_engine import teljesitmeny_szamitas
from portfolio_exposure import portfolio_exposure_szamitas
from market_data import arak_lekerese
from market_overview import market_overview_lekerese
from ai_analyst import portfolio_ai_elemzes
from watchlist import watchlist_lekerese
from watchlist_history import watchlist_tortenet
from stock_snapshot import stock_snapshot
from style import alkalmaz_style


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Bloomberg Lite",
    page_icon="📈",
    layout="wide"
)

alkalmaz_style()


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title(
    "AI Bloomberg Lite"
)

st.caption(
    "Portfolió elemzés • Piaci információk • Részvényelemzés"
)


# ---------------------------------------------------
# PORTFÓLIÓ ADATOK
# ---------------------------------------------------

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


# ---------------------------------------------------
# PORTFOLIO EXPOSURE
# ---------------------------------------------------

(
    theme_exposure,
    currency_exposure,
    asset_class_exposure
) = portfolio_exposure_szamitas(
    portfolio
)


# ---------------------------------------------------
# TRANZAKCIÓK / PERFORMANCE
# ---------------------------------------------------

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
) * 100


# ---------------------------------------------------
# PERFORMANCE DISPLAY
# ---------------------------------------------------

performance_display = (
    performance.copy()
)

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
            lambda x: f"${x:,.2f}"
        )


# ---------------------------------------------------
# RISK SCORE
# ---------------------------------------------------

score, szint, uzenetek = (
    risk_score_szamitas(
        portfolio
    )
)


# ---------------------------------------------------
# WATCHLIST SESSION STATE
# ---------------------------------------------------

if "watchlist_tickerek" not in st.session_state:

    st.session_state.watchlist_tickerek = [
        "NVDA",
        "AAPL",
        "MSFT",
        "TSLA",
        "AMD",
        "META"
    ]


# ---------------------------------------------------
# TABOK
# ---------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "💼 Portfolió",
    "👀 Piaci adatok",
    "🔎 Részvényelemzés",
    "🤖 AI Asszisztens"
])


# ===================================================
# TAB 1 — PORTFOLIO
# ===================================================

with tab1:

    st.subheader(
        "Portfolió Áttekintés"
    )


    # ------------------------------------------------
    # KPI
    # ------------------------------------------------

    col1, col2, col3, col4 = (
        st.columns(4)
    )

    with col1:

        st.metric(
            "💰 Portfólió érték",
            f"{teljes_ertek / 1_000_000:.2f} M Ft"
        )

    with col2:

        st.metric(
            "📦 Pozíciók száma",
            f"{len(portfolio)} db"
        )

    with col3:

        st.metric(
            "🌍 Devizák",
            f"{portfolio['Deviza'].nunique()} db"
        )

    with col4:

        st.metric(
            "⚠️ Legnagyobb súly",
            f"{legnagyobb['Súly %']:.2f}%"
        )


    st.divider()


    # ------------------------------------------------
    # FŐ DASHBOARD
    # ------------------------------------------------

    left_col, right_col = (
        st.columns(
            [1, 1]
        )
    )


    # ------------------------------------------------
    # BAL OLDAL
    # ------------------------------------------------

    with left_col:

        st.subheader(
            "📊 Portfólió összetétel"
        )

        st.dataframe(
            portfolio,
            width="stretch"
        )


        st.subheader(
            "🥧 Eszközallokáció"
        )

        fig = px.pie(
            portfolio,
            values="HUF érték",
            names="Eszköz",
            hole=0.45
        )

        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#1f2937",
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


    # ------------------------------------------------
    # JOBB OLDAL
    # ------------------------------------------------

    with right_col:

        st.subheader(
            "📈 Portfólió történeti teljesítmény"
        )

        tortenet = portfolio_tortenet(
            portfolio
        )

        fig_portfolio_history = px.line(
            tortenet,
            x=tortenet.index,
            y="Portfolio"
        )

        fig_portfolio_history.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#1f2937",
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10
            ),
            xaxis=dict(
                title="",
                showgrid=False
            ),
            yaxis=dict(
                title="",
                gridcolor="#e5e7eb"
            ),
            showlegend=False
        )

        fig_portfolio_history.update_traces(
            line=dict(
                width=3
            )
        )

        st.plotly_chart(
            fig_portfolio_history,
            width="stretch"
        )


        st.subheader(
            "🧠 Risk Overview"
        )

        risk_col1, risk_col2 = (
            st.columns(2)
        )

        with risk_col1:

            st.metric(
                "Risk Score",
                f"{score}/100"
            )

        with risk_col2:

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
    # PORTFOLIó ÖSSZETÉTEL
    # =================================================

    st.subheader(
        "🧩 Portfolió Összetétel"
    )

    st.caption(
        "Az aktuális portfólióérték alapján számított kitettségek."
    )


    exp1, exp2, exp3 = (
        st.columns(3)
    )


    # ------------------------------------------------
    # SZEKTOR MEGOSZLÁS
    # ------------------------------------------------

    with exp1:

        st.markdown(
            "#### Szektor Megoszlás"
        )

        fig_theme = px.pie(
            theme_exposure,
            values="HUF érték",
            names="Theme",
            hole=0.55
        )

        fig_theme.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#1f2937",
            margin=dict(
                l=5,
                r=5,
                t=10,
                b=10
            ),
            showlegend=True
        )

        st.plotly_chart(
            fig_theme,
            width="stretch"
        )

        for _, sor in (
            theme_exposure.iterrows()
        ):

            st.write(
                f"**{sor['Theme']}** "
                f"{sor['Súly %']:.1f}%"
            )


    # ------------------------------------------------
    # DEVIZA MEGOSZLÁS
    # ------------------------------------------------

    with exp2:

        st.markdown(
            "#### Deviza Megoszlás"
        )

        fig_currency = px.pie(
            currency_exposure,
            values="HUF érték",
            names="Deviza",
            hole=0.55
        )

        fig_currency.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#1f2937",
            margin=dict(
                l=5,
                r=5,
                t=10,
                b=10
            ),
            showlegend=True
        )

        st.plotly_chart(
            fig_currency,
            width="stretch"
        )

        for _, sor in (
            currency_exposure.iterrows()
        ):

            st.write(
                f"**{sor['Deviza']}** "
                f"{sor['Súly %']:.1f}%"
            )


    # ------------------------------------------------
    # ESZKÖZ OSZTÁLY MEGOSZLÁS
    # ------------------------------------------------

    with exp3:

        st.markdown(
            "#### Eszközosztály Megoszlás"
        )

        fig_asset = px.pie(
            asset_class_exposure,
            values="HUF érték",
            names="Asset Class",
            hole=0.55
        )

        fig_asset.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font_color="#1f2937",
            margin=dict(
                l=5,
                r=5,
                t=10,
                b=10
            ),
            showlegend=True
        )

        st.plotly_chart(
            fig_asset,
            width="stretch"
        )

        for _, sor in (
            asset_class_exposure.iterrows()
        ):

            st.write(
                f"**{sor['Asset Class']}** "
                f"{sor['Súly %']:.1f}%"
            )


    st.divider()


    # ------------------------------------------------
    # NAPI TELJESÍTMÉNY
    # ------------------------------------------------

    st.subheader(
        "📈 Mai piaci teljesítmény"
    )

    napi_adatok = (
        portfolio_napi_teljesitmeny(
            portfolio
        )
    )

    cols = st.columns(
        len(napi_adatok)
    )

    for col, adat in zip(
        cols,
        napi_adatok
    ):

        with col:

            valtozas = adat[
                "Napi változás %"
            ]

            st.metric(
                adat["Eszköz"],
                f"{valtozas:.2f}%"
            )


    # ------------------------------------------------
    # KONCENTRÁCIÓ
    # ------------------------------------------------

    if legnagyobb["Súly %"] > 40:

        st.error(
            f"⚠️ Magas koncentráció: "
            f"{legnagyobb['Eszköz']} "
            f"({legnagyobb['Súly %']:.2f}%)"
        )

    else:

        st.success(
            "✅ A portfólió megfelelően diverzifikált."
        )


    st.divider()


    # =================================================
    # PORTFOLIÓ TELJESÍTMÉNY
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
            "Befektetett összeg",
            f"${befektetett:,.2f}"
        )


    with perf2:

        st.metric(
            "Jelenlegi Érték",
            f"${aktualis:,.2f}"
        )


    with perf3:

        profit_delta = (
            f"{profit:+,.2f}"
        )

        st.metric(
            "P/L",
            f"${profit:,.2f}",
            profit_delta
        )


    with perf4:

        st.metric(
            "Teljes hozam",
            f"{hozam:+.2f}%"
        )


    st.markdown(
        "#### Position Performance"
    )

    st.dataframe(
        performance_display,
        width="stretch"
    )


# ===================================================
# TAB 2 — MARKETS
# ===================================================

with tab2:

    # ------------------------------------------------
    # MARKET OVERVIEW
    # ------------------------------------------------

    st.subheader(
        "🌎 Market Overview"
    )

    st.caption(
        "Equities • Volatility • Rates • Commodities • Crypto"
    )


    market_adatok = (
        market_overview_lekerese()
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
                        f"{adat['Napi változás %']:.2f}%"
                    )
                )


    else:

        st.warning(
            "A Market Overview adatok jelenleg nem érhetők el."
        )


    st.divider()


    # ------------------------------------------------
    # WATCHLIST
    # ------------------------------------------------

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

            if st.session_state.watchlist_tickerek:

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
                    f"{adat['Napi változás %']:.2f}%"
                )


    st.divider()


    # ------------------------------------------------
    # PRICE CHART
    # ------------------------------------------------

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
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            ),
            xaxis=dict(
                showgrid=False
            ),
            yaxis=dict(
                gridcolor="#e5e7eb"
            )
        )


        fig_watchlist.update_traces(
            line=dict(
                width=3
            )
        )


        st.plotly_chart(
            fig_watchlist,
            width="stretch"
        )


# ===================================================
# TAB 3 — EQUITY RESEARCH
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


    # ------------------------------------------------
    # COMPANY HEADER
    # ------------------------------------------------

    st.markdown(
        f"## {snapshot['Név']}"
    )

    st.caption(
        snapshot["Ticker"]
    )


    # ------------------------------------------------
    # MARKET OVERVIEW
    # ------------------------------------------------

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
            f"{snapshot['Napi változás %']:.2f}%"
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


    # ------------------------------------------------
    # VALUATION
    # ------------------------------------------------

    st.markdown(
        "### 📊 Valuation"
    )

    val1, val2, val3, val4 = (
        st.columns(4)
    )


    with val1:

        trailing_pe = snapshot[
            "P/E"
        ]

        st.metric(
            "P/E",
            (
                f"{trailing_pe:.2f}x"
                if trailing_pe is not None
                else "N/A"
            )
        )


    with val2:

        forward_pe = snapshot[
            "Forward P/E"
        ]

        st.metric(
            "Forward P/E",
            (
                f"{forward_pe:.2f}x"
                if forward_pe is not None
                else "N/A"
            )
        )


    with val3:

        ps = snapshot[
            "P/S"
        ]

        st.metric(
            "P/S",
            (
                f"{ps:.2f}x"
                if ps is not None
                else "N/A"
            )
        )


    with val4:

        ev_ebitda = snapshot[
            "EV/EBITDA"
        ]

        st.metric(
            "EV/EBITDA",
            (
                f"{ev_ebitda:.2f}x"
                if ev_ebitda is not None
                else "N/A"
            )
        )


    val5, val6, val7 = (
        st.columns(3)
    )


    with val5:

        pb = snapshot[
            "P/B"
        ]

        st.metric(
            "P/B",
            (
                f"{pb:.2f}x"
                if pb is not None
                else "N/A"
            )
        )


    with val6:

        eps = snapshot[
            "EPS"
        ]

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


    st.caption(
        "Valuation Screen: egyszerű, szektorsemleges "
        "P/E, P/S és EV/EBITDA alapú értékelés. "
        "Nem célár vagy DCF-alapú fair value."
    )


    st.divider()


    # ------------------------------------------------
    # PRICE RANGE
    # ------------------------------------------------

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
# TAB 4 — INTELLIGENCE
# ===================================================

with tab4:

    st.subheader(
        "🤖 AI Portfolio Analyst"
    )

    ai_elemzes = portfolio_ai_elemzes(
        portfolio,
        performance,
        score
    )

    for uzenet in ai_elemzes:

        st.write(
            uzenet
        )