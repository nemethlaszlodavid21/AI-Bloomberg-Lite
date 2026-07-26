import pandas as pd

# Portfólió adatok

portfolio = {
    "Eszköz": ["CSPX", "EQQQ", "SMH", "BTC"],
    "Érték": [1500000, 800000, 500000, 200000]
}

# DataFrame létrehozása

df = pd.DataFrame(portfolio)


# Teljes portfólió érték

osszes_vagyon = df["Érték"].sum()


# Súly számítása

df["Súly %"] = df["Érték"] / osszes_vagyon * 100

df["Súly %"] = df["Súly %"].round(2)


print(df)

print("\nTeljes portfólió:")
print(osszes_vagyon, "Ft")


# Legnagyobb pozíció keresése

legnagyobb = df.loc[df["Súly %"].idxmax()]

print("\nLegnagyobb pozíció:")
print(legnagyobb["Eszköz"], "-", legnagyobb["Súly %"], "%")


# Kockázati értékelés

if legnagyobb["Súly %"] > 40:
    print("⚠️ Figyelem: magas koncentrációs kockázat!")
else:
    print("✅ A portfólió megfelelően diverzifikált.")


# Automatikus befektetési riport

print("\nAI Portfolio Report")

print(
    "A portfólió teljes értéke",
    f"{osszes_vagyon:,}",
    "Ft."
)

print(
    "A legnagyobb pozíció:",
    legnagyobb["Eszköz"],
    "amely",
    legnagyobb["Súly %"],
    "% súlyt képvisel."
)

if legnagyobb["Súly %"] > 40:
    print(
        "Értékelés: a portfólió koncentrációs kockázatot tartalmaz."
    )
else:
    print(
        "Értékelés: a portfólió diverzifikációja megfelelő."
    )    