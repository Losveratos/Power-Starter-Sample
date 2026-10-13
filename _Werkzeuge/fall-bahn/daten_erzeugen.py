#!/usr/bin/env python3
"""Schreibt die Offline-Daten für 05-Fall-Bahn und die Kontrollzahlen.

Quelle der Fahrten pro Kopf: Eurostat 2024, wie in der Knowledge-Kitchen-Infografik
„Die Schweiz fährt Europa davon" (zugfahrten-europa-2024.html, auf eine Nachkommastelle gerundet).
Ländercodes wie bei Eurostat (Griechenland = EL, nicht GR).
Die Zielwerte in 3-Ziele sind ausgedacht (Übungsdaten), alles andere sind öffentliche Fakten.

Aufruf aus dem Repo-Root: python3 _Werkzeuge/fall-bahn/daten_erzeugen.py
"""
import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FALL = ROOT / "05-Fall-Bahn" / "Daten"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bahnhoefe_kreuztabelle  # noqa: E402
import bordgastronomie  # noqa: E402

# Code, Land, Land (engl.), Region (UN-Gliederung), EU-Mitglied, Fahrten pro Kopf 2024
LAENDER = [
    ("CH", "Schweiz", "Switzerland", "Westeuropa", "Nein", 57.9),
    ("LU", "Luxemburg", "Luxembourg", "Westeuropa", "Ja", 46.2),
    ("AT", "Österreich", "Austria", "Westeuropa", "Ja", 35.6),
    ("DK", "Dänemark", "Denmark", "Nordeuropa", "Ja", 35.2),
    ("DE", "Deutschland", "Germany", "Westeuropa", "Ja", 35.1),
    ("HU", "Ungarn", "Hungary", "Osteuropa", "Ja", 31.9),
    ("SE", "Schweden", "Sweden", "Nordeuropa", "Ja", 23.9),
    ("NL", "Niederlande", "Netherlands", "Westeuropa", "Ja", 20.9),
    ("PT", "Portugal", "Portugal", "Südeuropa", "Ja", 20.5),
    ("FR", "Frankreich", "France", "Westeuropa", "Ja", 19.2),
    ("CZ", "Tschechien", "Czechia", "Osteuropa", "Ja", 17.5),
    ("FI", "Finnland", "Finland", "Nordeuropa", "Ja", 15.0),
    ("NO", "Norwegen", "Norway", "Nordeuropa", "Nein", 14.7),
    ("IT", "Italien", "Italy", "Südeuropa", "Ja", 14.3),
    ("ES", "Spanien", "Spain", "Südeuropa", "Ja", 14.2),
    ("SK", "Slowakei", "Slovakia", "Osteuropa", "Ja", 13.3),
    ("PL", "Polen", "Poland", "Osteuropa", "Ja", 10.9),
    ("LV", "Lettland", "Latvia", "Nordeuropa", "Ja", 10.4),
    ("IE", "Irland", "Ireland", "Nordeuropa", "Ja", 9.4),
    ("SI", "Slowenien", "Slovenia", "Südeuropa", "Ja", 7.4),
    ("HR", "Kroatien", "Croatia", "Südeuropa", "Ja", 6.4),
    ("EE", "Estland", "Estonia", "Nordeuropa", "Ja", 5.8),
    ("RO", "Rumänien", "Romania", "Osteuropa", "Ja", 3.7),
    ("BG", "Bulgarien", "Bulgaria", "Osteuropa", "Ja", 3.3),
    ("LT", "Litauen", "Lithuania", "Nordeuropa", "Ja", 1.8),
    ("EL", "Griechenland", "Greece", "Südeuropa", "Ja", 1.4),
    ("ME", "Montenegro", "Montenegro", "Südeuropa", "Nein", 1.4),
    ("RS", "Serbien", "Serbia", "Südeuropa", "Nein", 1.2),
    ("TR", "Türkei", "Türkiye", "Westasien", "Nein", 0.3),
    ("BA", "Bosnien und Herzegowina", "Bosnia and Herzegovina", "Südeuropa", "Nein", 0.1),
    ("MK", "Nordmazedonien", "North Macedonia", "Südeuropa", "Nein", 0.1),
]

# Kantone für die SBB-Daten: Kürzel, Name, Hauptsprache, Amtssprachen
KANTONE = [
    ("ZH", "Zürich", "Deutsch", "Deutsch"), ("BE", "Bern", "Deutsch", "Deutsch, Französisch"),
    ("LU", "Luzern", "Deutsch", "Deutsch"), ("UR", "Uri", "Deutsch", "Deutsch"),
    ("SZ", "Schwyz", "Deutsch", "Deutsch"), ("OW", "Obwalden", "Deutsch", "Deutsch"),
    ("NW", "Nidwalden", "Deutsch", "Deutsch"), ("GL", "Glarus", "Deutsch", "Deutsch"),
    ("ZG", "Zug", "Deutsch", "Deutsch"), ("FR", "Freiburg", "Französisch", "Französisch, Deutsch"),
    ("SO", "Solothurn", "Deutsch", "Deutsch"), ("BS", "Basel-Stadt", "Deutsch", "Deutsch"),
    ("BL", "Basel-Landschaft", "Deutsch", "Deutsch"), ("SH", "Schaffhausen", "Deutsch", "Deutsch"),
    ("AR", "Appenzell Ausserrhoden", "Deutsch", "Deutsch"), ("AI", "Appenzell Innerrhoden", "Deutsch", "Deutsch"),
    ("SG", "St. Gallen", "Deutsch", "Deutsch"), ("GR", "Graubünden", "Deutsch", "Deutsch, Rätoromanisch, Italienisch"),
    ("AG", "Aargau", "Deutsch", "Deutsch"), ("TG", "Thurgau", "Deutsch", "Deutsch"),
    ("TI", "Tessin", "Italienisch", "Italienisch"), ("VD", "Waadt", "Französisch", "Französisch"),
    ("VS", "Wallis", "Französisch", "Französisch, Deutsch"), ("NE", "Neuenburg", "Französisch", "Französisch"),
    ("GE", "Genf", "Französisch", "Französisch"), ("JU", "Jura", "Französisch", "Französisch"),
]

ZIEL_JAHRE = [2026, 2027, 2028, 2029, 2030]
ZIEL_WACHSTUM = 0.03          # fiktiv: +3 % pro Jahr ab 2024
ZIEL_MINDEST_2030 = 5.0       # fiktiv: Länder unter 5 Fahrten sollen 2030 mindestens 5 erreichen


def de(v, nk=1):
    return f"{v:.{nk}f}".replace(".", ",")


def kategorie(v):
    return "hoch" if v >= 20 else ("mittel" if v >= 12 else "niedrig")


def ziel(v, jahr):
    z = v * (1 + ZIEL_WACHSTUM) ** (jahr - 2024)
    if jahr == 2030:
        z = max(z, ZIEL_MINDEST_2030)
    return round(z, 1)


def schreibe(pfad, kopf, zeilen):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    with pfad.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\r\n")
        w.writerow(kopf)
        w.writerows(zeilen)


def main():
    # Rohdaten: bewusst in Großbuchstaben wie auf der Infografik, Komma als Dezimalzeichen
    schreibe(FALL / "1-Rohdaten" / "zugfahrten_pro_kopf_2024.csv",
             ["geo", "Land", "Jahr", "Fahrten pro Kopf"],
             [(c, n.upper(), 2024, de(v)) for c, n, *_, v in LAENDER])
    schreibe(FALL / "2-Anreicherung" / "dim_land.csv",
             ["Code", "Land", "Land_EN", "Region", "EU"],
             [(c, n, e, r, eu) for c, n, e, r, eu, _ in LAENDER])
    schreibe(FALL / "2-Anreicherung" / "dim_kanton.csv",
             ["Kanton", "Kantonsname", "Hauptsprache", "Amtssprachen"], KANTONE)
    schreibe(FALL / "3-Ziele" / "ziele_fahrten_pro_kopf_fiktiv.csv",
             ["Land", *map(str, ZIEL_JAHRE)],
             [(n, *(de(ziel(v, j)) for j in ZIEL_JAHRE)) for _, n, *_, v in LAENDER])

    werte = {c: v for c, *_, v in LAENDER}
    name = {c: n for c, n, *_ in LAENDER}
    reihe = sorted(LAENDER, key=lambda t: -t[5])
    ziele_2030 = {c: ziel(v, 2030) for c, *_, v in LAENDER}
    regionen = sorted({t[3] for t in LAENDER})
    k = {
        "quelle": "Eurostat 2024, Zugfahrten pro Kopf, via Knowledge-Kitchen-Infografik",
        "zeilen_rohdaten": len(LAENDER),
        "summe_fahrten_pro_kopf": round(sum(werte.values()), 1),
        "durchschnitt": round(statistics.mean(werte.values()), 2),
        "median": statistics.median(werte.values()),
        "median_land": [name[c] for c, v in werte.items() if v == statistics.median(werte.values())],
        "top3": [(name[c], v) for c, *_, v in reihe[:3]],
        "rang_deutschland": [t[0] for t in reihe].index("DE") + 1,
        "faktor_schweiz_zu_deutschland": round(werte["CH"] / werte["DE"], 2),
        "kategorien": {kat: sum(1 for v in werte.values() if kategorie(v) == kat) for kat in ("hoch", "mittel", "niedrig")},
        "eu": {"anzahl": sum(1 for t in LAENDER if t[4] == "Ja"),
               "durchschnitt": round(statistics.mean(t[5] for t in LAENDER if t[4] == "Ja"), 2)},
        "nicht_eu": {"anzahl": sum(1 for t in LAENDER if t[4] == "Nein"),
                     "durchschnitt": round(statistics.mean(t[5] for t in LAENDER if t[4] == "Nein"), 2)},
        "regionen": {r: {"anzahl": sum(1 for t in LAENDER if t[3] == r),
                         "durchschnitt": round(statistics.mean(t[5] for t in LAENDER if t[3] == r), 2)}
                     for r in regionen},
        "ziele": {"zeilen_entpivotiert": len(LAENDER) * len(ZIEL_JAHRE),
                  "ziel_2030_deutschland": ziele_2030["DE"], "ziel_2030_schweiz": ziele_2030["CH"],
                  "ziel_2030_durchschnitt": round(statistics.mean(ziele_2030.values()), 2),
                  "luecke_2030_deutschland": round(ziele_2030["DE"] - werte["DE"], 1)},
        "kantone": len(KANTONE),
        "bahnhoefe_kreuztabelle": bahnhoefe_kreuztabelle.main(),
        "bordgastronomie": bordgastronomie.main(),
    }
    (FALL / "kontrollzahlen.json").write_text(json.dumps(k, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(k, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
