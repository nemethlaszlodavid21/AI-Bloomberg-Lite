# AI Bloomberg Lite

Python alapú személyes befektetési és portfólióelemző alkalmazás.

A projekt célja egy olyan egyszerű pénzügyi dashboard létrehozása, amely egy helyen kezeli a portfólió adatait, a piaci árfolyamokat, a teljesítményt és a kockázati mutatókat.

## Funkciók

* Portfólió importálás
* Pozíciók összesítése
* Portfólió értékének számítása
* Eszközallokáció és pozíciók súlyozása
* Aktuális piaci árak lekérése
* Napi teljesítmény számítása
* Historikus teljesítmény elemzése
* Tranzakciók feldolgozása
* Kockázati pontszám
* Automatikus pénzügyi számítások

## Market Data

Az alkalmazás aktuális piaci adatokat használ az árfolyamok frissítéséhez.

A piaci adatok kezelése külön `market_data.py` modulban történik. A rendszer kezeli a London Stock Exchange-en előforduló GBX árfolyamokat is, és GBP-re konvertálja azokat.

## Projekt felépítése

AI_Bloomberg_Lite/
│
├── app.py
├── market_data.py
├── portfolio.py
├── portfolio_analysis.py
├── portfolio_value.py
├── performance.py
├── performance_engine.py
├── risk.py
├── transactions.py
│
├── data/
└── README.md

## Használt technológiák

* Python
* Pandas
* Yahoo Finance
* Git / GitHub
* VS Code


## További fejlesztések

A projekt jelenleg fejlesztés alatt áll.

Tervezett funkciók:
* AI-alapú befektetési elemzés
* Vállalati pénzügyi elemzés
* Earnings és financial statement analysis
* DCF és egyéb értékelési modellek
* Automatikus piaci összefoglalók
* AI Investment Analyst funkciók
