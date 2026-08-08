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

# Cím

st.title("📈 AI Bloomberg Lite")

st.write("Saját befektetési portfólió elemző rendszer")


# Adatok betöltése

portfolio = portfolio_betoltes()


# Aktuális érték számítás

portfolio = portfolio_ertek_szamitas(portfolio)


# Elemzés

portfolio, teljes_ertek = portfolio_elemzes(portfolio)

legnagyobb = portfolio.loc[portfolio["Súly %"].idxmax()]

# KPI kártyák

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="💰 Portfólió érték",
        value=f"{teljes_ertek/1_000_000:.2f} M Ft"
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


# Táblázat

st.subheader("📊 Portfólió összetétel")

st.dataframe(portfolio)

st.subheader("🥧 Portfólió megoszlás")

fig = px.pie(
    portfolio,
    values="HUF érték",
    names="Eszköz",
    title="Eszközallokáció"
)

st.plotly_chart(fig, use_container_width=True)


st.subheader("📈 Portfólió történeti teljesítmény")

tortenet = portfolio_tortenet(portfolio)

st.line_chart(
    tortenet["Portfolio"]
)


# Napi teljesítmény

st.subheader("📈 Mai piaci teljesítmény")

napi_adatok = portfolio_napi_teljesitmeny(portfolio)

cols = st.columns(len(napi_adatok))

for col, adat in zip(cols, napi_adatok):

    with col:

        valtozas = adat["Napi változás %"]

        st.metric(
            label=adat["Eszköz"],
            value=f"{valtozas:.2f}%"
        )


if legnagyobb["Súly %"] > 40:
    st.error(
        f"⚠️ Magas koncentráció: {legnagyobb['Eszköz']} ({legnagyobb['Súly %']:.2f}%)"
    )
else:
    st.success("✅ A portfólió megfelelően diverzifikált.")


# Portfolió Teljesítmény

st.subheader("📈 Portfolió Teljesítmény")


tranzakciok = tranzakciok_betoltese()

poziciok = pozicio_osszesites(tranzakciok)


# Élő piaci árak lekérése

aktualis_arok = arak_lekerese(
    poziciok["Ticker"].tolist()
)


performance = teljesitmeny_szamitas(
    poziciok,
    aktualis_arok
)


befektetett = performance["Bekerülési érték"].sum()

aktualis = performance["Aktuális érték"].sum()

profit = performance["Profit"].sum()

hozam = (profit / befektetett) * 100


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


st.dataframe(performance)

st.subheader("🧠 AI Risk Score")

score, szint, uzenetek = risk_score_szamitas(portfolio)

st.metric(
    "Kockázati pontszám",
    f"{score}/100"
)

st.write(szint)

for u in uzenetek:
    st.write(u)


st.subheader("🤖 AI Portfolio Analyst")

ai_elemzes = portfolio_ai_elemzes(
    portfolio,
    performance,
    score
)

for uzenet in ai_elemzes:
    st.write(uzenet)
