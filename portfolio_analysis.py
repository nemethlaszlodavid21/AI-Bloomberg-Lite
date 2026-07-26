def portfolio_elemzes(portfolio):

    teljes_ertek = portfolio["Érték"].sum()

    portfolio["Súly %"] = (
        portfolio["Érték"] / teljes_ertek * 100
    )

    return portfolio, teljes_ertek