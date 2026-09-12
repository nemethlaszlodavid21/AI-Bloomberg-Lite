import yfinance as yf
import pandas as pd


def portfolio_tortenet(portfolio):

    tortenet = pd.DataFrame()


    for index, sor in portfolio.iterrows():

        ticker = sor["Ticker"]
        darab = sor["Darab"]
        eszkoz = sor["Eszköz"]


        adat = yf.download(
            ticker,
            period="1y",
            auto_adjust=True,
            progress=False
        )


        if adat.empty:
            continue


        if isinstance(
            adat.columns,
            pd.MultiIndex
        ):

            adat.columns = (
                adat.columns
                .get_level_values(0)
            )


        if "Close" not in adat.columns:
            continue


        ertek = (
            adat["Close"]
            * darab
        )


        ertek.name = eszkoz


        if tortenet.empty:

            tortenet = (
                ertek.to_frame()
            )

        else:

            tortenet = (
                tortenet.join(
                    ertek,
                    how="outer"
                )
            )


    if tortenet.empty:

        return pd.DataFrame(
            columns=["Portfolio"]
        )


    # -----------------------------------------------
    # DÁTUM RENDEZÉS
    # -----------------------------------------------

    tortenet = (
        tortenet
        .sort_index()
    )


    # -----------------------------------------------
    # HIÁNYZÓ ÁRFOLYAMOK KEZELÉSE
    # -----------------------------------------------
    #
    # Ha egy eszköz adott napon nem kereskedett,
    # az utolsó ismert értékét használjuk.
    #
    # Ez megakadályozza, hogy a portfólió értéke
    # mesterségesen lezuhanjon.
    # -----------------------------------------------

    tortenet = (
        tortenet
        .ffill()
    )


    # -----------------------------------------------
    # KEZDŐ HIÁNYZÓ ADATOK ELTÁVOLÍTÁSA
    # -----------------------------------------------
    #
    # Csak attól a naptól számolunk portfólióértéket,
    # ahol minden pozícióhoz már van árfolyamadat.
    # -----------------------------------------------

    tortenet = (
        tortenet
        .dropna()
    )


    # -----------------------------------------------
    # PORTFÓLIÓ ÖSSZÉRTÉK
    # -----------------------------------------------

    tortenet["Portfolio"] = (
        tortenet.sum(
            axis=1
        )
    )


    return tortenet