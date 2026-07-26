import matplotlib.pyplot as plt


# Portfólió adatok

eszkozok = ["CSPX", "EQQQ", "SMH", "BTC"]

sulyok = [50, 26.67, 16.67, 6.67]


# Diagram létrehozása

plt.figure(figsize=(7,7))


plt.pie(
    sulyok,
    labels=eszkozok,
    autopct="%1.1f%%"
)


plt.title("AI Bloomberg Lite - Portfólió megoszlás")


plt.show()