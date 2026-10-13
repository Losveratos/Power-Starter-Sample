# Daten · Fall Bahn in Europa

| Ordner | Datei | Inhalt |
|---|---|---|
| `1-Rohdaten` | `zugfahrten_pro_kopf_2024.csv` | Zugfahrten pro Kopf 2024, 31 Länder (Eurostat, Werte wie in der Kitchen-Infografik) – UTF-8, Semikolon, Komma als Dezimalzeichen |
| | `bordgastronomie_2025/` (12 Dateien) | **Demo Bordgastronomie:** eine Datei je Monat, Umsatz je ICE-Fahrt, Crew, Bereich (Bistro/Restaurant), Kategorie und Steuersatz – 5 Linien ab Köln. Komplett **simuliert** (fiktive Zugnummern und Crew-Kennungen) |
| | `bahnhoefe_reisende_2025_kreuztabelle.csv` | **Demo-Kreuztabelle:** 96 deutsche Bahnhöfe × 12 Monate 2025, Reisende pro Monat, mit Stadt, Bundesland, Größenklasse – zum Erklären von Normalisierung und Sternschema. Monatswerte **simuliert** |
| `2-Anreicherung` | `dim_land.csv` · `dim_kanton.csv` | Länder mit Eurostat-Code (Griechenland = **EL**), Region, EU ja/nein · 26 Schweizer Kantone mit Sprache |
| `3-Ziele` | `ziele_fahrten_pro_kopf_fiktiv.csv` | **ausgedachte** Ziele 2026–2030 als Kreuztabelle – zum Entpivotieren |
| | `kontrollzahlen.json` | alle Zahlen aus der Anleitung |

Die SBB- und die Eurostat-Zeitreihe liegen **nicht** hier – die lädst du live aus der Quelle (Teil B und C der Anleitung).

**In Power BI laden:** Daten abrufen → **Web** → Anonym → Adresse + Unterordner + Dateiname:
```
https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/
```
z. B. `…/Daten/1-Rohdaten/zugfahrten_pro_kopf_2024.csv`.

**Quellen:** Eurostat (Weiterverwendung mit Quellenangabe erlaubt) · SBB Open Data. Erzeugt mit
[`_Werkzeuge/fall-bahn/daten_erzeugen.py`](../../_Werkzeuge/fall-bahn/daten_erzeugen.py).

Zurück zur [Anleitung](../README.md).
