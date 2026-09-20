"""Adatminőség- és lefedettség-ellenőrzés az AI Bloomberg Lite-hoz."""

from __future__ import annotations

from typing import Any
import pandas as pd


def _pct(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return max(0.0, min(100.0, numerator / denominator * 100.0))


def _numeric_coverage(df: pd.DataFrame | None, column: str) -> tuple[int, int, float]:
    if df is None or df.empty or column not in df.columns:
        return 0, 0, 0.0
    values = pd.to_numeric(df[column], errors="coerce")
    total = len(values)
    valid = int(values.notna().sum())
    return valid, total, _pct(valid, total)


def adatminoseg_elemzes(
    tranzakciok: pd.DataFrame | None = None,
    portfolio: pd.DataFrame | None = None,
    poziciok: pd.DataFrame | None = None,
    tortenet: pd.DataFrame | None = None,
    koltsegek: dict[str, Any] | None = None,
    benchmark_adatok: pd.DataFrame | None = None,
) -> dict[str, Any]:
    tranzakciok = tranzakciok if tranzakciok is not None else pd.DataFrame()
    portfolio = portfolio if portfolio is not None else pd.DataFrame()
    poziciok = poziciok if poziciok is not None else pd.DataFrame()
    tortenet = tortenet if tortenet is not None else pd.DataFrame()
    koltsegek = koltsegek or {}

    tranzakcio_db = len(tranzakciok)
    aktiv_pozicio_db = len(portfolio)
    historikus_napok = len(tortenet)

    if "HUF érték" in portfolio.columns:
        ar_values = pd.to_numeric(portfolio["HUF érték"], errors="coerce")
        ar_total = len(ar_values)
        ar_valid = int((ar_values.notna() & (ar_values >= 0)).sum())
        ar_lefedettseg = _pct(ar_valid, ar_total)
    else:
        ar_total = aktiv_pozicio_db
        ar_valid = 0
        ar_lefedettseg = 0.0 if ar_total else 100.0

    bekerules_valid, bekerules_total, bekerules_lefedettseg = _numeric_coverage(
        poziciok, "Bekerülési érték"
    )
    if bekerules_total == 0 and aktiv_pozicio_db == 0:
        bekerules_lefedettseg = 100.0

    fx_lefedettseg = koltsegek.get("fx_lefedettseg_pct")
    try:
        fx_lefedettseg = float(fx_lefedettseg)
    except (TypeError, ValueError):
        fx_lefedettseg = 100.0 if tranzakcio_db == 0 else 0.0

    fx_hianyzo_devizak = koltsegek.get("fx_hianyzo_devizak", []) or []

    benchmark_elerheto = bool(
        benchmark_adatok is not None
        and hasattr(benchmark_adatok, "empty")
        and not benchmark_adatok.empty
    )

    if historikus_napok >= 252:
        historikus_statusz = "Legalább 1 kereskedési év"
    elif historikus_napok >= 126:
        historikus_statusz = "6–12 hónap"
    elif historikus_napok > 0:
        historikus_statusz = "6 hónapnál rövidebb"
    else:
        historikus_statusz = "Nincs historikus adat"

    problemak = []
    if aktiv_pozicio_db > 0 and ar_lefedettseg < 100:
        problemak.append("hiányos piaci árfolyamadat")
    if tranzakcio_db > 0 and fx_lefedettseg < 100:
        problemak.append("hiányos FX-adat")
    if aktiv_pozicio_db > 0 and bekerules_lefedettseg < 100:
        problemak.append("hiányos bekerülési érték")
    if historikus_napok == 0 and aktiv_pozicio_db > 0:
        problemak.append("nincs historikus idősor")

    if not problemak:
        adatstatusz = "Teljes"
    elif len(problemak) == 1:
        adatstatusz = "Részleges"
    else:
        adatstatusz = "Korlátozott"

    megjegyzesek = []
    if historikus_napok and historikus_napok < 252:
        megjegyzesek.append(
            f"A kockázati mutatók {historikus_napok} napos mintán alapulnak; "
            "az évesített értékek érzékenyebbek lehetnek a rövid megfigyelési időszakra."
        )
    if fx_hianyzo_devizak:
        megjegyzesek.append(
            "Hiányzó historikus FX-adat: " + ", ".join(map(str, fx_hianyzo_devizak)) + "."
        )
    if aktiv_pozicio_db > 0 and bekerules_lefedettseg < 100:
        megjegyzesek.append(
            "Egyes pozícióknál a bekerülési érték nem teljes; részleges tranzakciós előzmény is okozhatja."
        )
    if not benchmark_elerheto and historikus_napok > 0:
        megjegyzesek.append(
            "A benchmark-adat jelenleg nem elérhető, ezért a benchmarkhoz kötött mutatók korlátozottak lehetnek."
        )

    return {
        "adatstatusz": adatstatusz,
        "tranzakciok_szama": tranzakcio_db,
        "aktiv_poziciok_szama": aktiv_pozicio_db,
        "historikus_napok": historikus_napok,
        "historikus_statusz": historikus_statusz,
        "arfolyam_lefedettseg_pct": ar_lefedettseg,
        "arfolyam_valid": ar_valid,
        "arfolyam_total": ar_total,
        "fx_lefedettseg_pct": fx_lefedettseg,
        "fx_hianyzo_devizak": fx_hianyzo_devizak,
        "bekerules_lefedettseg_pct": bekerules_lefedettseg,
        "bekerules_valid": bekerules_valid,
        "bekerules_total": bekerules_total,
        "benchmark_elerheto": benchmark_elerheto,
        "megjegyzesek": megjegyzesek,
    }
