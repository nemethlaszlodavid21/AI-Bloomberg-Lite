# AI Bloomberg Lite

Python-alapú befektetési, portfólióelemző és piaci információs alkalmazás.

Az AI Bloomberg Lite célja egy olyan moduláris pénzügyi dashboard létrehozása, amely tranzakciós adatokból építi fel a befektetési portfóliót, aktuális és historikus piaci adatokat használ, valamint teljesítmény-, kockázati, költség- és portfólióelemzéseket készít.

A projektet pénzügyi elemzési, adatfeldolgozási és Python-fejlesztési ismereteim gyakorlati bemutatására készítettem.

## Live Demo

**AI Bloomberg Lite:**
https://ai-bloomberg-lite.streamlit.app

## Fő workflow

Tranzakciók
     ↓
Portfólió
     ↓
Piaci adatok
     ↓
Teljesítmény és kockázat
     ↓
Portfólióelemzés
     ↓
AI Portfolio Analyst

A portfólió kizárólag a felhasználó által rögzített vagy importált tranzakciókból épül fel.

Az alkalmazás új munkamenetben üres portfólióval indul.

## Fő funkciók

### Portfolio Management

* BUY és SELL tranzakciók kézi rögzítése
* Interactive Brokers CSV import
* Excel tranzakciós sablon és import
* Tranzakciós napló
* Duplikált importok kezelése
* Pozíciók automatikus aggregálása
* Átlagos bekerülési ár számítása
* Készpénz kezelése
* Corporate action kezelés

### Portfolio Analytics

* Aktuális portfólióérték
* Eszközsúlyok és allokáció
* Nem realizált eredmény
* Historikus teljesítmény
* Napi hozamok
* Portfólió exposure
* ETF look-through elemzés
* Portfólió vs. benchmark összehasonlítás

### Risk Analytics

Az alkalmazás cash-flow-adjusted napi portfólióhozamokból számít kockázati mutatókat, így a BUY és SELL tranzakciók önmagukban nem torzítják a piaci teljesítményt.

Főbb mutatók:

* Annualizált volatilitás
* Maximum drawdown
* Beta
* Sharpe-ráta
* Sortino-ráta
* Historical Value at Risk (VaR)
* Portfólió Risk Score

### Transaction Cost Analytics

* Összes tranzakciós költség
* Átlagos tranzakciós díj
* BUY forgalom
* Költséghányad
* Díjak devizánként
* Historikus devizaárfolyamok használata
* FX-adatlefedettség

### Market Intelligence

* Aktuális piaci adatok
* Személyre szabható watchlist
* Napi árfolyamváltozások
* Historikus árfolyamgrafikonok
* Piaci áttekintés
* Devizaárfolyam-kezelés

A piaci adatok lekérése gyorsítótárazott, így az alkalmazás nem tölti le feleslegesen ugyanazokat az adatokat minden újrafuttatáskor.

### Equity Research

Az alkalmazás külön részvényelemzési felületet tartalmaz, ahol egy kiválasztott vállalat aktuális piaci és részvényadatai vizsgálhatók.

### AI Portfolio Analyst

Az AI Portfolio Analyst a portfólió több elemzési rétegét egyesíti:

* portfólióstruktúra
* koncentráció
* exposure
* készpénzarány
* teljesítmény
* kockázat
* tranzakciós költségek
* adatminőség

A modul célja, hogy a különálló pénzügyi mutatókat strukturált portfólióértékeléssé alakítsa.

### Data Quality & Coverage

Az alkalmazás külön ellenőrzi az elemzések mögött álló adatok minőségét és lefedettségét.

Vizsgált területek többek között:

* piaci ár lefedettség
* FX lefedettség
* bekerülési érték lefedettség
* benchmark adatok
* historikus adatsor hossza
* részleges tranzakciós előzmények

Ez segít elkülöníteni a számítási eredményeket azoktól az esetektől, amikor az alapul szolgáló adatok hiányosak.

## Adatarchitektúra

Kézi tranzakció ──────┐
                      │
IBKR CSV ─────────────┼──→ SQLite adatbázis
                      │          ↓
Excel import ─────────┘    Portfolio Engine
                                 ↓
                    ┌────────────┼────────────┐
                    ↓            ↓            ↓
              Performance      Risk       Exposure
                    │            │            │
                    └────────────┼────────────┘
                                 ↓
                       AI Portfolio Analyst

A tranzakciós adatbázis az alkalmazás központi adatforrása.

## Adatvédelem

A publikus alkalmazás munkamenetenként elkülönített lokális SQLite adatbázist használ.

Egy új felhasználói munkamenet üres portfólióval indul, így az alkalmazás nem tartalmaz előre betöltött személyes portfólióadatokat.

A repository nem tartalmaz személyes CSV-, Excel- vagy adatbázisfájlokat.

## Market Data

Az alkalmazás a Yahoo Finance adatait használja aktuális és historikus piaci információk lekérésére.

A rendszer többek között kezeli:

* részvényeket
* ETF-eket
* devizaárfolyamokat
* benchmarkokat
* London Stock Exchange instrumentumokat
* GBX → GBP árkonverziót

A gyakran használt piaci adatok cache-elése csökkenti a szükségtelen API-lekéréseket és gyorsítja a felhasználói felületet.

## Technológiák

* **Python**
* **Pandas**
* **NumPy**
* **Streamlit**
* **Plotly**
* **Matplotlib**
* **SQLite**
* **Yahoo Finance / yfinance**
* **OpenPyXL**
* **Git / GitHub**

## Projektstruktúra

A projekt moduláris felépítésű. A főbb komponensek:

AI_Bloomberg_Lite/
│
├── app.py
│
├── portfolio_database.py
├── portfolio_engine.py
├── portfolio_history.py
├── portfolio_benchmark.py
├── portfolio_exposure.py
├── portfolio_holdings.py
├── portfolio_value.py
│
├── risk_analytics.py
├── transaction_costs.py
├── data_quality.py
│
├── market_data.py
├── market_overview.py
├── fx_data.py
│
├── watchlist.py
├── watchlist_history.py
├── stock_snapshot.py
│
├── ibkr_import.py
├── excel_import.py
├── corporate_actions.py
│
├── ai_portfolio_analyst.py
│
├── requirements.txt
└── README.md

## Projekt célja

Az AI Bloomberg Lite egy folyamatosan fejlesztett pénzügyi portfólióprojekt.

A fejlesztés során többek között az alábbi területeken szerzek és alkalmazok gyakorlati tapasztalatot:

* pénzügyi adatelemzés
* portfólióelemzés
* kockázati mutatók
* tranzakciós adatok feldolgozása
* Python és Pandas
* adatbázis-kezelés
* API-alapú piaci adatok
* adatvizualizáció
* pénzügyi dashboardok
* AI-alapú pénzügyi elemzési logika

A hosszú távú cél egy könnyen használható, moduláris **AI-alapú befektetési és pénzügyi elemző rendszer** továbbfejlesztése.

---

**Live application:** https://ai-bloomberg-lite.streamlit.app
