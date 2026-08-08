import feedparser


def hirek_lekerese():

    feedek = {
        "US Markets": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",
        "Technology": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=QQQ&region=US&lang=en-US",
        "Bitcoin": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=BTC-USD&region=US&lang=en-US"
    }

    hirek = []

    for kategoria, url in feedek.items():

        feed = feedparser.parse(url)

        for entry in feed.entries[:5]:

            hirek.append({
                "Kategória": kategoria,
                "Cím": entry.get("title", ""),
                "Link": entry.get("link", ""),
                "Dátum": entry.get("published", "")
            })

    return hirek


def hir_relevancia(hir, portfolio):

    szoveg = hir["Cím"].lower()

    eredmenyek = []

    eszkozok = [
        str(x).upper()
        for x in portfolio["Eszköz"]
    ]

    # -------------------------
    # CSPX
    # -------------------------

    if "CSPX" in eszkozok:

        if any(kulcsszo in szoveg for kulcsszo in [
            "s&p 500",
            "s&p500",
            "sp500"
        ]):

            eredmenyek.append({
                "Eszköz": "CSPX",
                "Pontszám": 3,
                "Szint": "HIGH"
            })

        elif any(kulcsszo in szoveg for kulcsszo in [
            "us equities",
            "us stocks",
            "american stocks",
            "american equities"
        ]):

            eredmenyek.append({
                "Eszköz": "CSPX",
                "Pontszám": 2,
                "Szint": "MEDIUM"
            })


    # -------------------------
    # EQQQ
    # -------------------------

    if "EQQQ" in eszkozok:

        if any(kulcsszo in szoveg for kulcsszo in [
            "nasdaq",
            "nasdaq 100"
        ]):

            eredmenyek.append({
                "Eszköz": "EQQQ",
                "Pontszám": 3,
                "Szint": "HIGH"
            })

        elif any(kulcsszo in szoveg for kulcsszo in [
            "technology stocks",
            "tech stocks"
        ]):

            eredmenyek.append({
                "Eszköz": "EQQQ",
                "Pontszám": 3,
                "Szint": "HIGH"
            })

        elif any(kulcsszo in szoveg for kulcsszo in [
            "apple",
            "microsoft",
            "amazon",
            "alphabet",
            "meta"
        ]):

            eredmenyek.append({
                "Eszköz": "EQQQ",
                "Pontszám": 2,
                "Szint": "MEDIUM"
            })


    # -------------------------
    # SMH
    # -------------------------

    if "SMH" in eszkozok:

        if any(kulcsszo in szoveg for kulcsszo in [
            "semiconductor",
            "semiconductors",
            "chipmaker",
            "chipmakers",
            "chip stocks"
        ]):

            eredmenyek.append({
                "Eszköz": "SMH",
                "Pontszám": 3,
                "Szint": "HIGH"
            })

        elif any(kulcsszo in szoveg for kulcsszo in [
            "nvidia",
            "amd",
            "broadcom",
            "tsmc"
        ]):

            eredmenyek.append({
                "Eszköz": "SMH",
                "Pontszám": 3,
                "Szint": "HIGH"
            })


    # -------------------------
    # BTC
    # -------------------------

    if "BTC" in eszkozok:

        if any(kulcsszo in szoveg for kulcsszo in [
            "bitcoin",
            "btc"
        ]):

            eredmenyek.append({
                "Eszköz": "BTC",
                "Pontszám": 3,
                "Szint": "HIGH"
            })

        elif any(kulcsszo in szoveg for kulcsszo in [
            "cryptocurrency",
            "crypto",
            "digital assets"
        ]):

            eredmenyek.append({
                "Eszköz": "BTC",
                "Pontszám": 2,
                "Szint": "MEDIUM"
            })


    return eredmenyek