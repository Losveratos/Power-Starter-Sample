#!/usr/bin/env python3
"""Demo-Daten Bordgastronomie 2025: 12 Monatsdateien mit Umsätzen je ICE-Fahrt, Crew, Bereich und Kategorie.

Alles ist SIMULIERT (fiktive Zugnummern, fiktive Crew-Kennungen, keine Personen), aber an der Wirklichkeit
orientiert:
  - fünf ICE-Linien ab Köln Hbf, je drei Zugpaare pro Tag, mit typischer Baureihe,
  - Bordrestaurant nur in Baureihen, die eins haben (ICE 1, ICE 4) – ICE 3M und ICE 3 neo haben nur ein Bistro,
  - Steuersatz 2025: Speisen im Bistro (Mitnahme) 7 %, Speisen im Restaurant (Verzehr am Platz) 19 %,
    Getränke immer 19 % – auch im Bistro,
  - mehr Umsatz auf langen Fahrten, freitags und sonntags, im Sommer und vor Weihnachten,
    Alkohol vor allem abends und am Wochenende, Frühstück/Kaffee morgens,
  - etwa 2 % der Fahrten ohne Umsatz (Bistro geschlossen oder Zug ausgefallen) – fehlen in der Datei.

Wird von daten_erzeugen.py aufgerufen, geht aber auch allein:
  python3 _Werkzeuge/fall-bahn/bordgastronomie.py
"""
import calendar
import csv
import datetime as dt
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORDNER = ROOT / "05-Fall-Bahn" / "Daten" / "1-Rohdaten" / "bordgastronomie_2025"
JAHR = 2025
SEED = 2510

# Linie, Ziel, Fahrzeit Köln ↔ Ziel (h), ICE-Typ, Baureihe, Restaurant ja/nein,
# Zugnummern ab Köln, Zugnummern nach Köln (fiktiv), Abfahrtszeiten
LINIEN = [
    ("Köln – Frankfurt – München", "München Hbf", 4.6, "ICE 3neo", "BR 408", False,
     ["ICE 511", "ICE 515", "ICE 519"], ["ICE 510", "ICE 514", "ICE 518"], ["06:55", "12:55", "17:55"]),
    ("Köln – Hannover – Berlin", "Berlin Hbf", 4.4, "ICE 4", "BR 412", True,
     ["ICE 641", "ICE 645", "ICE 649"], ["ICE 640", "ICE 644", "ICE 648"], ["07:48", "13:48", "18:48"]),
    ("Köln – Aachen – Brüssel", "Brüssel-Süd", 1.9, "ICE 3M", "BR 406", False,
     ["ICE 11", "ICE 15", "ICE 17"], ["ICE 10", "ICE 14", "ICE 16"], ["08:43", "14:43", "18:43"]),
    ("Köln – Dortmund – Hamburg", "Hamburg-Altona", 4.1, "ICE 4", "BR 412", True,
     ["ICE 923", "ICE 927", "ICE 931"], ["ICE 922", "ICE 926", "ICE 930"], ["07:10", "11:10", "16:10"]),
    ("Köln – Mannheim – Basel", "Basel SBB", 4.2, "ICE 1", "BR 401", True,
     ["ICE 101", "ICE 105", "ICE 109"], ["ICE 100", "ICE 104", "ICE 108"], ["06:20", "11:20", "16:20"]),
]

# Bordgastro-Teams (fiktive Kennungen, keine Personen) je Standort; Leistungsfaktor ±
STANDORTE = {"Köln": ("KOE", 10), "Berlin": ("BER", 5), "München": ("MUC", 5), "Hamburg": ("HAM", 5),
             "Basel": ("BAS", 4), "Brüssel": ("BRU", 3)}
ZIEL_STANDORT = {"München Hbf": "München", "Berlin Hbf": "Berlin", "Brüssel-Süd": "Brüssel",
                 "Hamburg-Altona": "Hamburg", "Basel SBB": "Basel"}

KATEGORIEN = ["Getränke", "Alkoholische Getränke", "Snacks", "Mahlzeiten"]
# Ø Bruttopreis je Artikel
PREIS = {("Bistro", "Getränke"): 3.90, ("Bistro", "Alkoholische Getränke"): 5.40,
         ("Bistro", "Snacks"): 4.60, ("Bistro", "Mahlzeiten"): 11.90,
         ("Restaurant", "Getränke"): 4.30, ("Restaurant", "Alkoholische Getränke"): 6.20,
         ("Restaurant", "Mahlzeiten"): 16.90}
# Artikel pro Fahrstunde und Bereich (Grundniveau, voll besetzter Zug am Dienstag im März)
ARTIKEL_PRO_STUNDE = {("Bistro", "Getränke"): 26, ("Bistro", "Alkoholische Getränke"): 5,
                      ("Bistro", "Snacks"): 11, ("Bistro", "Mahlzeiten"): 7,
                      ("Restaurant", "Getränke"): 7, ("Restaurant", "Alkoholische Getränke"): 3,
                      ("Restaurant", "Mahlzeiten"): 5}
# Ohne Restaurant wandern Gäste ins Bistro
BISTRO_ZUSCHLAG_OHNE_RESTAURANT = {"Getränke": 1.15, "Alkoholische Getränke": 1.35, "Snacks": 1.10, "Mahlzeiten": 1.45}

MONAT = [0.88, 0.90, 0.96, 1.00, 1.03, 1.06, 1.10, 1.10, 1.02, 1.00, 0.97, 1.08]   # Auslastung
WOCHENTAG = [0.95, 0.92, 0.93, 0.98, 1.15, 0.98, 1.12]                              # Mo … So


def steuersatz(bereich, kategorie):
    if kategorie in ("Getränke", "Alkoholische Getränke"):
        return 19
    return 7 if bereich == "Bistro" else 19


def tageszeit_faktor(abfahrt, kategorie, wochenende):
    stunde = int(abfahrt[:2])
    if kategorie == "Alkoholische Getränke":
        f = 0.35 if stunde < 11 else (0.9 if stunde < 16 else 1.6)
        return f * (1.25 if wochenende else 1.0)
    if kategorie == "Getränke":
        return 1.25 if stunde < 11 else 1.0           # Kaffee am Morgen
    if kategorie == "Mahlzeiten":
        return 0.8 if stunde < 11 else (1.2 if stunde < 15 else 1.05)
    return 1.0


def crews(rng):
    teams = {}
    for ort, (kurz, n) in STANDORTE.items():
        for i in range(1, n + 1):
            teams[f"BG-{kurz}-{i:02d}"] = (ort, rng.uniform(0.92, 1.08))
    return teams


def fahrten():
    for linie, ziel, dauer, typ, br, rest, hin, rueck, zeiten in LINIEN:
        for nr, ab in zip(hin, zeiten):
            yield nr, linie, "Köln Hbf", ziel, ab, dauer, typ, br, rest
        for nr, ab in zip(rueck, zeiten):
            # Gegenzug: um die halbe Umlaufzeit versetzt
            h, m = map(int, ab.split(":"))
            zurueck = (h + 1) % 24
            yield nr, linie, ziel, "Köln Hbf", f"{zurueck:02d}:{m:02d}", dauer, typ, br, rest


def main():
    rng = random.Random(SEED)
    teams = crews(rng)
    team_je_ort = defaultdict(list)
    for code, (ort, _) in teams.items():
        team_je_ort[ort].append(code)

    kopf = ["Datum", "Wochentag", "Zugnummer", "Linie", "Von", "Nach", "Abfahrt", "ICE-Typ", "Baureihe",
            "Crew", "Crew-Standort", "Bereich", "Kategorie", "Steuersatz", "Anzahl Artikel",
            "Umsatz netto", "MwSt", "Umsatz brutto"]
    tage_de = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    k = {"dateien": 12, "zeilen": 0, "fahrten": 0, "ausgefallene_fahrten": 0, "netto": 0.0, "brutto": 0.0,
         "netto_je_monat": {}, "netto_je_linie": defaultdict(float), "netto_je_bereich": defaultdict(float),
         "netto_je_kategorie": defaultdict(float), "netto_je_steuersatz": defaultdict(float), "crews": len(teams)}
    ORDNER.mkdir(parents=True, exist_ok=True)

    for monat in range(1, 13):
        zeilen, netto_monat = [], 0.0
        for d in range(1, calendar.monthrange(JAHR, monat)[1] + 1):
            tag = dt.date(JAHR, monat, d)
            wt = tag.weekday()
            for nr, linie, von, nach, ab, dauer, typ, br, rest in fahrten():
                if rng.random() < 0.02:          # Bistro zu oder Zug fällt aus → keine Zeilen
                    k["ausgefallene_fahrten"] += 1
                    continue
                k["fahrten"] += 1
                ort = rng.choice(["Köln", ZIEL_STANDORT[nach if von == "Köln Hbf" else von]])
                crew = rng.choice(team_je_ort[ort])
                leistung = teams[crew][1]
                last = MONAT[monat - 1] * WOCHENTAG[wt] * rng.uniform(0.85, 1.15)
                if (monat, d) in ((12, 24), (12, 25), (12, 31), (1, 1)):
                    last *= 0.6
                for bereich in (["Bistro", "Restaurant"] if rest else ["Bistro"]):
                    for kat in KATEGORIEN:
                        if (bereich, kat) not in ARTIKEL_PRO_STUNDE:
                            continue                       # Snacks gibt es nur am Bistrotresen
                        menge = ARTIKEL_PRO_STUNDE[(bereich, kat)] * dauer * last * leistung
                        menge *= tageszeit_faktor(ab, kat, wt >= 4)
                        if bereich == "Bistro" and not rest:
                            menge *= BISTRO_ZUSCHLAG_OHNE_RESTAURANT[kat]
                        anzahl = max(0, round(menge * rng.uniform(0.9, 1.1)))
                        if anzahl == 0:
                            continue
                        satz = steuersatz(bereich, kat)
                        brutto = round(anzahl * PREIS[(bereich, kat)] * rng.uniform(0.94, 1.06), 2)
                        netto = round(brutto / (1 + satz / 100), 2)
                        mwst = round(brutto - netto, 2)
                        zeilen.append([tag.strftime("%d.%m.%Y"), tage_de[wt], nr, linie, von, nach, ab, typ, br,
                                       crew, teams[crew][0], bereich, kat, f"{satz} %", anzahl,
                                       f"{netto:.2f}".replace(".", ","), f"{mwst:.2f}".replace(".", ","),
                                       f"{brutto:.2f}".replace(".", ",")])
                        netto_monat += netto
                        k["brutto"] += brutto
                        k["netto_je_linie"][linie] += netto
                        k["netto_je_bereich"][bereich] += netto
                        k["netto_je_kategorie"][kat] += netto
                        k["netto_je_steuersatz"][f"{satz} %"] += netto
        pfad = ORDNER / f"bordgastronomie_{JAHR}-{monat:02d}.csv"
        with pfad.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";", lineterminator="\r\n")
            w.writerow(kopf)
            w.writerows(zeilen)
        k["zeilen"] += len(zeilen)
        k["netto"] += netto_monat
        k["netto_je_monat"][f"{JAHR}-{monat:02d}"] = round(netto_monat, 2)

    for key in ("netto", "brutto"):
        k[key] = round(k[key], 2)
    for key in ("netto_je_linie", "netto_je_bereich", "netto_je_kategorie", "netto_je_steuersatz"):
        k[key] = {a: round(b, 2) for a, b in sorted(k[key].items(), key=lambda t: -t[1])}
    return k


if __name__ == "__main__":
    import json
    print(json.dumps(main(), ensure_ascii=False, indent=2))
