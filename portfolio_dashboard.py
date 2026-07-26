import pandas as pd
import matplotlib.pyplot as plt


# Portfólió adatok

portfolio = {
    "Eszköz": ["CSPX", "EQQQ", "SMH", "BTC"],
    "Érték": [1500000, 800000, 500000, 200000]
}


# Pandas DataFrame

df = pd.DataFrame(portfolio)


# Teljes portfólió érték

osszes_vagyon = df["Érték"].sum()


# Súly számítás

df["Súly %"] = df["Érték"] / osszes_vagyon * 100


# Kerekítés

df["Súly %"] = df["Súly %"].round(2)


print(df)


# Grafikon készítés

plt.figure(figsize=(7,7))


plt.pie(
    df["Súly %"],
    labels=df["Eszköz"],
    autopct="%1.1f%%"
)


# Oszlopdiagram

plt.figure(figsize=(8,5))

plt.bar(
    df["Eszköz"],
    df["Érték"] / 1000000
)

plt.title("AI Bloomberg Lite - Portfólió érték")

plt.xlabel("Eszköz")

plt.ylabel("Érték (millió Ft)")

# Értékek kiírása az oszlopokra

for i, ertek in enumerate(df["Érték"] / 1000000):
    plt.text(
        i,
        ertek,
        f"{ertek:.2f} M Ft",
        ha="center",
        va="bottom"
    )

plt.show()


plt.title("AI Bloomberg Lite - Portfólió Dashboard")


plt.show()