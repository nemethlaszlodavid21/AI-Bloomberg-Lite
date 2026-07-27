def risk_score_szamitas(portfolio):

    score = 100
    uzenetek = []

    for index, sor in portfolio.iterrows():

        suly = sor["Súly %"]
        eszkoz = sor["Eszköz"]

        if suly > 40:
            score -= 20
            uzenetek.append(
                f"⚠️ {eszkoz} súlya magas ({suly:.1f}%)"
            )

        elif suly > 25:
            score -= 10
            uzenetek.append(
                f"⚠️ {eszkoz} koncentráció ({suly:.1f}%)"
            )

    if score >= 80:
        szint = "🟢 Alacsony kockázat"

    elif score >= 60:
        szint = "🟠 Közepes kockázat"

    else:
        szint = "🔴 Magas kockázat"

    return score, szint, uzenetek