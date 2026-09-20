"""Szabályalapú, reprodukálható portfólióelemző az AI Bloomberg Lite-hoz."""

from __future__ import annotations

from typing import Any
import pandas as pd


def _num(value: Any):
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_numeric(row: pd.Series, preferred: tuple[str, ...] = ()):
    for col in preferred:
        if col in row.index:
            v = _num(row[col])
            if v is not None:
                return v
    for v in row.values:
        n = _num(v)
        if n is not None:
            return n
    return None


def _top_exposure(df: pd.DataFrame):
    if df is None or df.empty:
        return None
    work = df.copy()
    numeric = work.select_dtypes(include="number").columns.tolist()
    if not numeric:
        return None
    value_col = next((c for c in numeric if any(k in str(c).lower() for k in ("weight", "súly", "szaz", "száz", "%", "exposure"))), numeric[0])
    label_cols = [c for c in work.columns if c != value_col]
    if not label_cols:
        return None
    label_col = label_cols[0]
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[value_col]).sort_values(value_col, ascending=False)
    if work.empty:
        return None
    row = work.iloc[0]
    value = float(row[value_col])
    if 0 <= value <= 1:
        value *= 100
    return str(row[label_col]), value


def portfolio_elemzes_2(
    portfolio: pd.DataFrame,
    risk: dict | None = None,
    risk_score: float | None = None,
    hozam_pct: float | None = None,
    koltsegek: dict | None = None,
    sector_exposure: pd.DataFrame | None = None,
    currency_exposure: pd.DataFrame | None = None,
    cash_pct: float | None = None,
    history_days: int | None = None,
):
    """Strukturált elemzést ad vissza kizárólag a kiszámított app-adatokból."""
    risk = risk or {}
    koltsegek = koltsegek or {}
    sections: list[dict[str, Any]] = []

    # Portfólióstruktúra
    observations = []
    if portfolio is not None and not portfolio.empty:
        weight_col = next((c for c in portfolio.columns if str(c).lower() in {"súly", "suly", "weight", "weight %", "súly %"}), None)
        ticker_col = next((c for c in portfolio.columns if str(c).lower() in {"ticker", "symbol"}), None)
        if weight_col:
            w = pd.to_numeric(portfolio[weight_col], errors="coerce").dropna().sort_values(ascending=False)
            if not w.empty:
                if w.max() <= 1:
                    w = w * 100
                top3 = float(w.head(3).sum())
                observations.append(f"A három legnagyobb pozíció együttes súlya {top3:.1f}%.")
                if ticker_col:
                    idx = w.index[0]
                    observations.append(f"A legnagyobb egyedi pozíció {portfolio.loc[idx, ticker_col]} ({w.loc[idx]:.1f}%).")
        observations.append(f"Aktív pozíciók száma: {len(portfolio)}.")
    if cash_pct is not None:
        observations.append(f"Készpénz aránya: {cash_pct:.1f}%.")
    top_sector = _top_exposure(sector_exposure)
    if top_sector:
        observations.append(f"Legnagyobb szektorkitettség: {top_sector[0]} ({top_sector[1]:.1f}%).")
    top_ccy = _top_exposure(currency_exposure)
    if top_ccy:
        observations.append(f"Legnagyobb devizakitettség: {top_ccy[0]} ({top_ccy[1]:.1f}%).")
    sections.append({"title": "Portfólióstruktúra", "items": observations or ["Nincs elegendő adat a portfólióstruktúra elemzéséhez."]})

    # Kockázat
    risk_items = []
    metric_map = [
        ("Volatilitás %", "Évesített volatilitás", "%"),
        ("Max Drawdown %", "Maximális drawdown", "%"),
        ("Beta", "Beta az S&P 500-hoz képest", ""),
        ("Sharpe Ratio", "Sharpe-ráta", ""),
        ("Sortino Ratio", "Sortino-ráta", ""),
        ("VaR 95% %", "1 napos historikus VaR (95%)", "%"),
    ]
    for key, label, suffix in metric_map:
        v = _num(risk.get(key))
        if v is not None:
            risk_items.append(f"{label}: {abs(v) if key == 'VaR 95% %' else v:.2f}{suffix}.")
    rs = _num(risk_score)
    if rs is not None:
        risk_items.append(f"Belső Risk Score: {rs:.0f}/100.")
    if history_days:
        risk_items.append(f"A kockázati becslések {history_days} napnyi rendelkezésre álló historikus adatra épülnek.")
    sections.append({"title": "Kockázat", "items": risk_items or ["Nincs elegendő historikus adat a kockázati mutatókhoz."]})

    # Teljesítmény
    perf_items = []
    h = _num(hozam_pct)
    if h is not None:
        perf_items.append(f"A jelenlegi bekerülési értékhez viszonyított teljes hozam {h:+.2f}%.")
    sections.append({"title": "Teljesítmény", "items": perf_items or ["A teljesítmény jelenleg nem számítható."]})

    # Költségek
    cost_items = []
    total_fee = _num(koltsegek.get("osszes_dij_huf"))
    avg_fee = _num(koltsegek.get("atlag_dij_huf"))
    ratio = _num(koltsegek.get("koltseghanyad_pct"))
    coverage = _num(koltsegek.get("fx_lefedettseg_pct"))
    if total_fee is not None:
        cost_items.append(f"Összes tranzakciós díj: {total_fee:,.0f} Ft.")
    if avg_fee is not None:
        cost_items.append(f"Átlagos díj tranzakciónként: {avg_fee:,.0f} Ft.")
    if ratio is not None:
        cost_items.append(f"Költséghányad a BUY forgalomhoz viszonyítva: {ratio:.3f}%.")
    if coverage is not None:
        cost_items.append(f"Historikus FX-lefedettség: {coverage:.1f}%.")
    sections.append({"title": "Tranzakciós költségek", "items": cost_items or ["Nincs rendelkezésre álló tranzakciós költségadat."]})

    # Megfigyelések – leíró, nem befektetési ajánlás
    notes = []
    vol = _num(risk.get("Volatilitás %"))
    beta = _num(risk.get("Beta"))
    dd = _num(risk.get("Max Drawdown %"))
    if vol is not None:
        if vol >= 30:
            notes.append("A historikus volatilitás magas; a portfólió értéke rövid idő alatt jelentősen változhat.")
        elif vol >= 15:
            notes.append("A historikus volatilitás közepes tartományban van.")
        else:
            notes.append("A historikus volatilitás az eddigi mintában viszonylag alacsony.")
    if beta is not None:
        if beta > 1.15:
            notes.append("A historikus beta alapján a portfólió az S&P 500-nál érzékenyebben mozgott.")
        elif beta < 0.85:
            notes.append("A historikus beta alapján a portfólió az S&P 500-nál kevésbé érzékenyen mozgott.")
        else:
            notes.append("A historikus beta az S&P 500-hoz közeli piaci érzékenységet jelez.")
    if dd is not None:
        notes.append(f"A vizsgált időszak legnagyobb csúcs–mélypont visszaesése {abs(dd):.2f}% volt.")
    if top_sector and top_sector[1] >= 35:
        notes.append(f"A {top_sector[0]} szektor súlya koncentrációs kitettséget jelent ({top_sector[1]:.1f}%).")
    if ratio is not None and ratio >= 0.5:
        notes.append("A tranzakciós költségek a BUY forgalomhoz mérten érdemi súlyt képviselnek.")
    if history_days and history_days < 252:
        notes.append("A historikus minta egy évnél rövidebb, ezért a kockázati mutatók még érzékenyek lehetnek az egyedi piaci napokra.")
    sections.append({"title": "Fő megfigyelések", "items": notes or ["A jelenlegi adatok alapján nincs további kiemelt szabályalapú megfigyelés."]})

    return sections
