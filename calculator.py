# AI Bloomberg Lite
# Modul: egyszerű hozam kalkulátor
# Verzió: v0.1

befektetett_toke = 1000000
eves_hozam = 0.08

nyereseg = befektetett_toke * eves_hozam
vegso_ertek = befektetett_toke + nyereseg

print(f"Befektetett tőke: {befektetett_toke:,.0f} Ft")
print(f"Éves hozam: {eves_hozam * 100:.1f}%")
print(f"Nyereség: {nyereseg:,.0f} Ft")
print(f"Portfólió értéke év végén: {vegso_ertek:,.0f} Ft")