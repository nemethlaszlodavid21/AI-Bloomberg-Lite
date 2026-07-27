import streamlit as st
import plotly.express as px

from portfolio_import import portfolio_betoltes
from portfolio_analysis import portfolio_elemzes
from portfolio_value import portfolio_ertek_szamitas


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

if legnagyobb["Súly %"] > 40:
    st.error(
        f"⚠️ Magas koncentráció: {legnagyobb['Eszköz']} ({legnagyobb['Súly %']:.2f}%)"
    )
else:
    st.success("✅ A portfólió megfelelően diverzifikált.")

st.subheader("🤖 AI Portfolio Report")

st.write(
    f"""
A portfólió teljes értéke **{teljes_ertek:,.0f} Ft**.

A legnagyobb pozíció a **{legnagyobb['Eszköz']}**,
amely **{legnagyobb['Súly %']:.2f}%**-ot képvisel.

A jelenlegi portfólió mérsékelt koncentrációs kockázatot mutat.
"""
)