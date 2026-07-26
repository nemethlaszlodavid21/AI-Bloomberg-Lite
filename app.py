import streamlit as st

from portfolio_import import portfolio_betoltes
from portfolio_analysis import portfolio_elemzes


# Cím

st.title("📈 AI Bloomberg Lite")

st.write("Saját befektetési portfólió elemző rendszer")


# Adatok betöltése

portfolio = portfolio_betoltes()


# Elemzés

portfolio, teljes_ertek = portfolio_elemzes(portfolio)


# Fő érték

st.metric(
    label="💰 Teljes portfólió érték",
    value=f"{teljes_ertek:,.0f} Ft"
)


# Táblázat

st.subheader("📊 Portfólió összetétel")

st.dataframe(portfolio)

legnagyobb = portfolio.loc[portfolio["Súly %"].idxmax()]

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