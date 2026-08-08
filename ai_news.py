from openai import OpenAI
import os


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def hir_ai_elemzes(hir, relevanciak):

    eszkozok = ", ".join(
        [
            f"{x['Eszköz']} ({x['Szint']})"
            for x in relevanciak
        ]
    )

    prompt = f"""
Te egy professzionális befektetési elemző vagy.

Elemezd az alábbi pénzügyi hírt magyar nyelven.

HÍR:
{hir['Cím']}

KATEGÓRIA:
{hir['Kategória']}

ÉRINTETT PORTFÓLIÓESZKÖZÖK:
{eszkozok}

Feladat:

1. Adj egy rövid, természetes magyar címet.
2. Foglald össze a hírt 2-3 mondatban.
3. Határozd meg a várható portfólióhatást:
   - Pozitív
   - Negatív
   - Semleges
   - Bizonytalan
4. Egy mondatban magyarázd el, miért fontos a hír
   a portfólió szempontjából.

Ne adj befektetési tanácsot.
Ne találj ki olyan információt, amely nincs a hírben.

A választ pontosan ebben a formában add vissza:

CÍM:
...

ÖSSZEFOGLALÓ:
...

HATÁS:
...

MIÉRT FONTOS:
...
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text