def portfolio_ai_elemzes(
    portfolio,
    performance,
    score
):

    uzenetek = []

    # Legnagyobb pozíció
    legnagyobb = portfolio.loc[
        portfolio["Súly %"].idxmax()
    ]

    # Legjobb teljesítő
    legjobb = performance.loc[
        performance["Hozam %"].idxmax()
    ]

    # Legrosszabb teljesítő
    legrosszabb = performance.loc[
        performance["Hozam %"].idxmin()
    ]

    # Koncentráció
    if legnagyobb["Súly %"] > 40:

        uzenetek.append(
            f"⚠️ Magas koncentráció: "
            f"{legnagyobb['Eszköz']} "
            f"({legnagyobb['Súly %']:.1f}%)."
        )

    elif legnagyobb["Súly %"] > 25:

        uzenetek.append(
            f"🟠 Mérsékelt koncentráció: "
            f"{legnagyobb['Eszköz']} "
            f"({legnagyobb['Súly %']:.1f}%)."
        )

    else:

        uzenetek.append(
            "🟢 A portfólió koncentrációja jelenleg mérsékelt."
        )

    # Legjobb teljesítő

    uzenetek.append(
        f"📈 A legjobb teljesítő jelenleg "
        f"{legjobb['Eszköz']}, "
        f"{legjobb['Hozam %']:.2f}% hozammal."
    )

    # Legrosszabb teljesítő

    uzenetek.append(
        f"📉 A leggyengébb teljesítő "
        f"{legrosszabb['Eszköz']}, "
        f"{legrosszabb['Hozam %']:.2f}% hozammal."
    )

    # Risk Score

    if score >= 80:

        uzenetek.append(
            "🟢 A kockázati pontszám alapján "
            "a portfólió kockázata alacsony."
        )

    elif score >= 60:

        uzenetek.append(
            "🟠 A portfólió közepes kockázati szintet mutat."
        )

    else:

        uzenetek.append(
            "🔴 A portfólió magas kockázati szintet mutat."
        )

    return uzenetek