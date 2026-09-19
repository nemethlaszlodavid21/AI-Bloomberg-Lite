def risk_score_szamitas(portfolio):

    # 0 = alacsony kockázat
    # 100 = nagyon magas kockázat

    score = 0
    uzenetek = []

    if portfolio is None or portfolio.empty:
        return (
            0,
            "Nincs portfólióadat",
            []
        )

    # ==========================================
    # KONCENTRÁCIÓS KOCKÁZAT
    # ==========================================

    for _, sor in portfolio.iterrows():

        suly = float(sor["Súly %"])
        eszkoz = str(sor["Eszköz"])

        if suly >= 70:

            score += 60

            uzenetek.append(
                f"🔴 {eszkoz} extrém magas "
                f"portfóliósúlyt képvisel ({suly:.1f}%)."
            )

        elif suly >= 50:

            score += 45

            uzenetek.append(
                f"🔴 {eszkoz} súlya nagyon magas "
                f"({suly:.1f}%)."
            )

        elif suly >= 35:

            score += 30

            uzenetek.append(
                f"🟠 {eszkoz} súlya magas "
                f"({suly:.1f}%)."
            )

        elif suly >= 20:

            score += 15

            uzenetek.append(
                f"🟡 {eszkoz} jelentős koncentrációt "
                f"képvisel ({suly:.1f}%)."
            )

    # ==========================================
    # DIVERZIFIKÁCIÓ
    # ==========================================

    poziciok_szama = len(portfolio)

    if poziciok_szama == 1:

        score += 30

        uzenetek.append(
            "🔴 A portfólió mindössze egyetlen "
            "pozícióból áll."
        )

    elif poziciok_szama <= 3:

        score += 20

        uzenetek.append(
            f"🟠 A portfólió csak {poziciok_szama} "
            "pozícióból áll."
        )

    elif poziciok_szama <= 5:

        score += 10

        uzenetek.append(
            f"🟡 A portfólió {poziciok_szama} "
            "pozícióból áll, ezért a diverzifikáció "
            "korlátozott."
        )

    # ==========================================
    # SCORE MAXIMUM 100
    # ==========================================

    score = min(
        int(round(score)),
        100
    )

    # ==========================================
    # KOCKÁZATI SZINT
    # ==========================================

    if score <= 20:

        szint = "🟢 Alacsony kockázat"

    elif score <= 40:

        szint = "🟡 Mérsékelt kockázat"

    elif score <= 60:

        szint = "🟠 Közepes kockázat"

    elif score <= 80:

        szint = "🔴 Magas kockázat"

    else:

        szint = "🔴 Nagyon magas kockázat"

    return (
        score,
        szint,
        uzenetek
    )