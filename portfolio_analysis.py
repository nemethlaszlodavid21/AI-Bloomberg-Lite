def portfolio_elemzes(portfolio):

    teljes_ertek = portfolio["HUF érték"].sum()

    portfolio["Súly %"] = (
        portfolio["HUF érték"] / teljes_ertek * 100
    )

    return portfolio, teljes_ertek