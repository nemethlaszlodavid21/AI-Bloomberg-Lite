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
from market_data import arak_lekerese
from ai_analyst import portfolio_ai_elemzes
from watchlist import watchlist_lekerese
from watchlist_history import watchlist_tortenet
from stock_snapshot import stock_snapshot


# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Bloomberg Lite",
    page_icon="📈",
    layout="wide"
)


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.title("AI Bloomberg Lite")

st.caption(
    "Portfolio Analytics • Market Intelligence • Equity Research"
)


# ---------------------------------------------------
# ADATOK BETÖLTÉSE
# ---------------------------------------------------

portfolio = portfolio_betoltes()

portfolio = portfolio_ertek_szamitas(portfolio)

portfolio, teljes_ertek = portfolio_elemzes(portfolio)

legnagyobb = portfolio.loc[
    portfolio["Súly %"].idxmax()
]


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
    profit / befektetett
) * 100


# ---------------------------------------------------
# RISK SCORE
# ---------------------------------------------------

score, szint, uzenetek = risk_score_szamitas(
    portfolio
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
    "💼 Portfolio",
    "👀 Markets",
    "🔎 Equity Research",
    "🤖 Intelligence"
])


# ===================================================
# TAB 1 — PORTFOLIO
# ===================================================

with tab1:

    st.subheader("Portfolio Overview")

    # KPI kártyák

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Portfólió érték",
            value=f"{teljes_ertek / 1_000_000:.2f} M Ft"
        )

    with col2:
        st.metric(
            label="📦 Pozíciók száma",
            value=f"{len(portfolio)} db"
        )

    with col3:
        st.metric(
            label="🌍 Devizák",
            value=f"{portfolio['Deviza'].nunique()} db"
        )

    with col4:
        st.metric(
            label="⚠️ Legnagyobb súly",
            value=f"{legnagyobb['Súly %']:.2f}%"
        )


    st.divider()


    # Portfólió összetétel

    st.subheader("📊 Portfólió összetétel")

    st.dataframe(
        portfolio,
        width="stretch"
    )


    # Pie chart

    st.subheader("🥧 Eszközallokáció")

    fig = px.pie(
        portfolio,
        values="HUF érték",
        names="Eszköz",
        title="Portfólió megoszlás"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


    # Történeti teljesítmény

    st.subheader(
        "📈 Portfólió történeti teljesítmény"
    )

    tortenet = portfolio_tortenet(
        portfolio
    )

    st.line_chart(
        tortenet["Portfolio"]
    )


    # Napi teljesítmény

    st.subheader(
        "📈 Mai piaci teljesítmény"
    )

    napi_adatok = portfolio_napi_teljesitmeny(
        portfolio
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
                label=adat["Eszköz"],
                value=f"{valtozas:.2f}%"
            )


    # Koncentráció figyelmeztetés

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


    # Portfolio Performance

    st.subheader(
        "📈 Portfólió teljesítmény"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💰 Befektetett tőke",
            f"{befektetett:,.0f}"
        )

    with col2:

        st.metric(
            "📊 Aktuális érték",
            f"{aktualis:,.0f}"
        )

    with col3:

        st.metric(
            "💵 Profit",
            f"{profit:,.0f}"
        )

    with col4:

        st.metric(
            "📈 Hozam",
            f"{hozam:.2f}%"
        )


    st.dataframe(
        performance,
        width="stretch"
    )


    # Risk Score

    st.subheader(
        "🧠 Portfolio Risk Score"
    )

    st.metric(
        "Kockázati pontszám",
        f"{score}/100"
    )

    st.write(szint)

    for u in uzenetek:
        st.write(u)


# ===================================================
# TAB 2 — MARKETS
# ===================================================

with tab2:

    st.subheader(
        "👀 Market Watchlist"
    )


    # Watchlist kezelés

    with st.expander(
        "⚙️ Watchlist kezelése"
    ):

        uj_ticker = st.text_input(
            "Új ticker hozzáadása",
            placeholder="Pl. GOOGL"
        )

        col_add, col_remove = st.columns(2)


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

                    st.success(
                        f"{ticker} hozzáadva a Watchlisthez."
                    )

                    st.rerun()


        with col_remove:

            eltavolitando = st.selectbox(
                "Eltávolítandó ticker",
                st.session_state.watchlist_tickerek
            )

            if st.button(
                "🗑️ Eltávolítás"
            ):

                if (
                    eltavolitando
                    in st.session_state.watchlist_tickerek
                ):

                    st.session_state.watchlist_tickerek.remove(
                        eltavolitando
                    )

                    st.rerun()


    # Élő Watchlist adatok

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
                    label=adat["Ticker"],
                    value=f"${adat['Ár']:.2f}",
                    delta=f"{adat['Napi változás %']:.2f}%"
                )


    st.divider()


    # Árfolyamgrafikon

    st.subheader(
        "📈 Price Chart"
    )

    tickerek = [
        adat["Ticker"]
        for adat in watchlist
    ]


    if tickerek:

        kivalasztott_ticker = st.selectbox(
            "Válassz egy részvényt:",
            tickerek
        )

        # Elmentjük, hogy az Equity Research tab is használhassa

        st.session_state[
            "kivalasztott_ticker"
        ] = kivalasztott_ticker


        torteneti_adatok = watchlist_tortenet(
            kivalasztott_ticker
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

        st.plotly_chart(
            fig_watchlist,
            width="stretch"
        )


# ===================================================
# TAB 3 — EQUITY RESEARCH
# ===================================================

with tab3:

    st.subheader(
        "🔎 Stock Snapshot"
    )


    # Ha még nem választottunk tickert,
    # AAPL legyen az alapértelmezett

    elemzett_ticker = st.session_state.get(
        "kivalasztott_ticker",
        "AAPL"
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


    st.divider()


    # Első KPI sor

    col1, col2, col3 = st.columns(3)


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

            market_cap_trillion = (
                market_cap
                / 1_000_000_000_000
            )

            st.metric(
                "Market Cap",
                f"${market_cap_trillion:.2f}T"
            )

        else:

            st.metric(
                "Market Cap",
                "N/A"
            )


    with col3:

        pe = snapshot["P/E"]

        st.metric(
            "P/E",
            f"{pe:.2f}x"
            if pe
            else "N/A"
        )


    # Második KPI sor

    col4, col5, col6 = st.columns(3)


    with col4:

        st.metric(
            "52 hetes maximum",
            f"${snapshot['52W High']:.2f}"
        )


    with col5:

        st.metric(
            "52 hetes minimum",
            f"${snapshot['52W Low']:.2f}"
        )


    with col6:

        hozam_30d = snapshot[
            "30D hozam %"
        ]

        st.metric(
            "30 napos hozam",
            (
                f"{hozam_30d:.2f}%"
                if hozam_30d is not None
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