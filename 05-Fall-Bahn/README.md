# Fall · Bahn in Europa

**Für Bahn-Leute: Power-BI-Grundlagen an echten, öffentlichen Bahndaten – etwa 1½ Stunden, drei Teile.**

Wer fährt in Europa am meisten Zug? Welche Bahnhöfe der Schweiz sind am vollsten? Und wie haben sich
die Fahrgastzahlen seit 2004 entwickelt? Die Fragen beantwortest du mit **offenen Daten** von Eurostat und der SBB.
Dabei übst du die Grundlagen aus [Tag 1](../01-Tag-1/) und [Tag 2](../02-Tag-2/): laden, aufräumen, Beziehungen,
Measures, Entpivotieren.

> ⬇️ **Alles in einem Paket:** [Anleitung als PDF + Daten + Skripte (ZIP)](https://github.com/Losveratos/Power-Starter-24-25-September/raw/main/00-Downloads/Fall-Bahn-Europa.zip)

| Teil | Frage | Daten | Du übst | Dauer |
|---|---|---|---|---|
| **A** | Wer fährt in Europa am meisten Zug? | Eurostat 2024, liegt hier im Repo | CSV laden, Gebietsschema, bedingte Spalte, Beziehung, Measures, Entpivotieren | 40 min |
| **B** | Welche Bahnhöfe sind am vollsten? | SBB, **live** aus dem SBB-Datenportal | große echte Tabelle, Karte, Top 10, „Was misst die Zahl?" | 25 min |
| **C** | Wie entwickeln sich die Fahrgäste seit 2004? | Eurostat, **live** über die Eurostat-Schnittstelle | echte Kreuztabelle entpivotieren, Zeitreihe, Summenzeilen | 25 min |

**Teil A funktioniert immer** (die Daten liegen hier). Teil B und C holen die Daten direkt bei SBB und Eurostat –
dafür muss dein Netz diese Seiten erlauben. Wenn nicht: siehe 🆘 in Teil B.

---

## Bevor du anfängst

**Du brauchst:** Power BI Desktop auf Windows ([Installation: Tag 1, Übung 0](../01-Tag-1/README.md#übung-0--power-bi-desktop-installieren-15-min))
und Internet. Neue leere Datei: **Datei → Neu**. Zwischendurch speichern (**Strg + S**).

| Zeichen | Bedeutung |
|---|---|
| ✅ **Kontrollpunkt** | Diese Zahl muss bei dir stehen. |
| 🆘 **Hängst du fest?** | Häufige Fehler und wie du sie behebst. |
| ⏭ **Überspringen** | Fertiges Skript für diesen Schritt – einfügen, Kontrollzahl prüfen, weiter. |
| 📚 **Mehr dazu** | [Knowledge Kitchen](https://datenwgknowledgekitchen.com/) und Microsoft Learn zum Nachlesen. |

**So fügst du ein fertiges Skript ein (⏭):** **Start → Daten transformieren** → im Power-Query-Editor
**Neue Quelle → Leere Abfrage** → **Erweiterter Editor** → alles markieren, Skript einfügen → **Fertig** →
rechts unter **Eigenschaften → Name** den Namen aus der ersten Zeile des Skripts eintragen.

Alle Kontrollzahlen stehen auch in [`Daten/kontrollzahlen.json`](Daten/kontrollzahlen.json).

### Was liegt hier?

| Ordner | Inhalt |
|---|---|
| [`Daten/1-Rohdaten/`](Daten/1-Rohdaten/) | `zugfahrten_pro_kopf_2024.csv` – Zugfahrten pro Kopf, 31 Länder (Eurostat 2024) |
| [`Daten/2-Anreicherung/`](Daten/2-Anreicherung/) | `dim_land.csv` (Name, Region, EU ja/nein) · `dim_kanton.csv` (26 Schweizer Kantone) |
| [`Daten/3-Ziele/`](Daten/3-Ziele/) | `ziele_fahrten_pro_kopf_fiktiv.csv` – **ausgedachte** Ziele 2026–2030 als Kreuztabelle |
| [`Loesungen/PowerQuery/`](Loesungen/PowerQuery/) | M-Code für jeden Ladeschritt |
| [`Loesungen/DAX/`](Loesungen/DAX/) | alle Measures mit Kontrollzahlen |

Basis-Adresse für **Daten abrufen → Web** (Anmeldung **Anonym**):
```
https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/
```

---

## Teil A · Wer fährt in Europa am meisten Zug?

Die Idee stammt aus der Knowledge-Kitchen-Infografik
**[„Die Schweiz fährt Europa davon"](https://datenwgknowledgekitchen.com/zugfahrten-infografik.html)** – schau sie dir kurz an,
am Ende von Teil A hast du dieselben Zahlen selbst in Power BI.

### A1 · Die Zugfahrten laden (10 min)

1. **Start → Daten abrufen → Web** → Adresse einfügen → **OK** → **Anonym → Verbinden**:
   ```
   https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/1-Rohdaten/zugfahrten_pro_kopf_2024.csv
   ```
2. In der Vorschau **Daten transformieren** (nicht *Laden*).
3. Abfrage rechts unter **Name** in `fakt_zugfahrten` umbenennen.
4. Die Spalte `Land` (Namen in GROSSBUCHSTABEN) brauchst du nicht: **Rechtsklick → Entfernen**. Den schönen Namen holst du gleich aus `dim_land`.
5. Spalte `Fahrten pro Kopf`: auf das Symbol links im Spaltenkopf klicken → **Mithilfe des Gebietsschemas…** →
   Datentyp **Dezimalzahl**, Gebietsschema **Deutsch (Deutschland)** → **OK**.
6. **Spalte hinzufügen → Bedingte Spalte**, Name `Kategorie`:
   *Wenn* `Fahrten pro Kopf` *ist größer oder gleich* `20` → `hoch` ·
   **Klausel hinzufügen**: *größer oder gleich* `12` → `mittel` · *Sonst* `niedrig` → **OK**.

> ✅ **Kontrollpunkt:** 31 Zeilen. Oben steht **CH** mit **57,9**, unten **MK** mit **0,1**.
> In der Spalte `Kategorie`: 9 × hoch, 7 × mittel, 15 × niedrig (Pfeil im Spaltenkopf zeigt die Werte).

> 🆘 **Hängst du fest?**
> - **Aus 57,9 wird 579:** Schritt 5 wurde mit Gebietsschema *Englisch* gemacht. Im Bereich **Angewendete Schritte** den Typ-Schritt löschen und Schritt 5 wiederholen.
> - **Umlaute kaputt (Ã–STERREICH):** Unter **Quelle** (Zahnrad) den **Dateiursprung** auf **65001: Unicode (UTF-8)** stellen.
> - **Bedingte Spalte bietet „größer oder gleich" nicht an:** Die Spalte ist noch Text – erst Schritt 5.
> - ⏭ **Überspringen:** [`01_fakt_zugfahrten.pq`](Loesungen/PowerQuery/01_fakt_zugfahrten.pq)

> 📚 **Mehr dazu:** [Praxis-Pfad · Modul 1 Daten anbinden](https://datenwgknowledgekitchen.com/powerbi_praxis_pfad.html#modul-1) und
> [Modul 2 Aufräumen](https://datenwgknowledgekitchen.com/powerbi_praxis_pfad.html#modul-2) ·
> Microsoft Learn: [Datentypen in Power Query](https://learn.microsoft.com/de-de/power-query/data-types) ·
> [Web-Connector](https://learn.microsoft.com/de-de/power-query/connectors/web/web)

### A2 · Die Länder dazuholen (10 min)

1. Genauso laden (**Neue Quelle → Web**), Name `dim_land`:
   ```
   https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/2-Anreicherung/dim_land.csv
   ```
2. **Schließen & übernehmen**.
3. Links auf **Modellansicht** (drittes Symbol) → `fakt_zugfahrten[geo]` auf `dim_land[Code]` ziehen.
   Power BI schlägt **n:1** (viele zu eins) vor → **Speichern**.

> ✅ **Kontrollpunkt:** Eine Linie zwischen den Tabellen, **1** bei `dim_land`, **\*** bei `fakt_zugfahrten`.
> Tabelle mit `dim_land[Region]` und `fakt_zugfahrten[Fahrten pro Kopf]`: Power BI **summiert** – Westeuropa zeigt 214,9.
> Das ist Unsinn (Fahrten pro Kopf addiert man nicht). Deshalb gleich ein Measure.

> 🆘 **Hängst du fest?**
> - **Beziehung wird 1:1 oder m:n:** Du hast falsch herum gezogen oder eine andere Spalte erwischt. Linie doppelt anklicken und Spalten prüfen.
> - **Griechenland fehlt später:** Eurostat schreibt Griechenland als **EL**, nicht GR. Beide Dateien hier nutzen EL – bei eigenen Daten darauf achten.
> - ⏭ **Überspringen:** [`02a_dim_land.pq`](Loesungen/PowerQuery/02a_dim_land.pq)

> 📚 **Mehr dazu:** [Einsteiger-Guide · Datenmodell](https://datenwgknowledgekitchen.com/power_bi_einsteiger_guide_v4.html#model) ·
> Microsoft Learn: [Sternschema](https://learn.microsoft.com/de-de/power-bi/guidance/star-schema) ·
> [Beziehungen verstehen](https://learn.microsoft.com/de-de/power-bi/transform-model/desktop-relationships-understand)

### A3 · Die ersten Measures (10 min)

1. **Start → Daten eingeben** → Tabelle `_Measures` nennen → **Laden**.
2. `_Measures` markieren → **Tabellentools → Neues Measure** → Formel eintippen → **Enter**. So für alle vier:
   ```DAX
   Fahrten pro Kopf = AVERAGE ( fakt_zugfahrten[Fahrten pro Kopf] )
   ```
   ```DAX
   Median Europa = CALCULATE ( MEDIAN ( fakt_zugfahrten[Fahrten pro Kopf] ), REMOVEFILTERS ( dim_land ) )
   ```
   ```DAX
   Abstand zum Median = [Fahrten pro Kopf] - [Median Europa]
   ```
   ```DAX
   Rang = IF ( NOT ISBLANK ( [Fahrten pro Kopf] ), RANKX ( ALL ( dim_land[Land] ), [Fahrten pro Kopf], , DESC ) )
   ```
3. **Tabelle** mit `dim_land[Land]`, `Fahrten pro Kopf`, `Abstand zum Median`, `Rang` bauen, nach `Rang` sortieren.

> ✅ **Kontrollpunkt:** Gesamtzeile **15,45** · Median **13,3** (das ist die Slowakei) ·
> **Deutschland Rang 5, Abstand +21,8** · Schweiz Rang 1 mit 57,9.
> Tabelle mit `dim_land[EU]`: **Ja 16,80** (24 Länder) · **Nein 10,81** (7 Länder).

> 🆘 **Hängst du fest?**
> - **Überall Rang 1:** In `RANKX` steht `ALL ( dim_land[Land] )` – die Tabelle muss auch `dim_land[Land]` zeigen, nicht eine Spalte aus `fakt_zugfahrten`.
> - **Gesamt 15,45 – ist das „Europa"?** Nein: Es ist der Durchschnitt der Länder, Luxemburg zählt so viel wie Deutschland. Ein echter Europa-Wert braucht Einwohner – ein schönes Diskussionsthema.
> - ⏭ **Überspringen:** alle Measures in [`measures.dax`](Loesungen/DAX/measures.dax)

> 📚 **Mehr dazu:** [Einsteiger-Guide · DAX](https://datenwgknowledgekitchen.com/power_bi_einsteiger_guide_v4.html#dax) ·
> Microsoft Learn: [Measures erstellen](https://learn.microsoft.com/de-de/power-bi/transform-model/desktop-tutorial-create-measures) ·
> [CALCULATE](https://learn.microsoft.com/de-de/dax/calculate-function-dax)

### A4 · Ziele entpivotieren (10 min)

Die Ziele kommen – wie so oft – als Kreuztabelle: eine Zeile je Land, eine Spalte je Jahr. **Die Zahlen sind ausgedacht** (+3 % pro Jahr).

1. **Start → Daten transformieren → Neue Quelle → Web**, Name `ziele`:
   ```
   https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/3-Ziele/ziele_fahrten_pro_kopf_fiktiv.csv
   ```
2. Spalte `Land` markieren → **Rechtsklick → Andere Spalten entpivotieren**.
3. `Attribut` in `Jahr` umbenennen (Typ **Ganze Zahl**), `Wert` in `Ziel` (Typ **Dezimalzahl**, Gebietsschema **Deutsch (Deutschland)** wie in A1).
4. **Schließen & übernehmen** → Modellansicht → `ziele[Land]` auf `dim_land[Land]` ziehen (n:1).
5. Zwei Measures:
   ```DAX
   Ziel 2030 = CALCULATE ( AVERAGE ( ziele[Ziel] ), ziele[Jahr] = 2030 )
   ```
   ```DAX
   Lücke zum Ziel 2030 = [Ziel 2030] - [Fahrten pro Kopf]
   ```

> ✅ **Kontrollpunkt:** vorher 31 Zeilen × 6 Spalten, nachher **155 Zeilen × 3 Spalten**.
> Deutschland: **Ziel 2030 = 41,9, Lücke 6,8** · Schweiz 69,1 · Gesamt 19,39.

> 🆘 **Hängst du fest?**
> - **Nur noch eine Spalte „Wert" mit 31 Zeilen:** Du hast *Spalten entpivotieren* auf `Land` statt *Andere Spalten entpivotieren* gewählt. Schritt löschen, noch einmal.
> - **Beziehung über `Land` geht nicht:** Die Ziele haben keinen Code, nur den Namen. Die Namen in `dim_land` sind eindeutig – das reicht hier. Achte auf den gleichen Datentyp (Text).
> - ⏭ **Überspringen:** [`03_ziele_entpivotieren.pq`](Loesungen/PowerQuery/03_ziele_entpivotieren.pq)

> 📚 **Mehr dazu:** Microsoft Learn: [Spalten entpivotieren](https://learn.microsoft.com/de-de/power-query/unpivot-column)

**Seitenidee Teil A:** Balkendiagramm `dim_land[Land]` × `Fahrten pro Kopf` (absteigend sortiert), Farbe nach `fakt_zugfahrten[Kategorie]`,
daneben eine Karte mit `Median Europa` und ein Datenschnitt `dim_land[Region]`. Vergleiche mit der [Kitchen-Infografik](https://datenwgknowledgekitchen.com/zugfahrten-infografik.html).

---

## Teil B · Welche Bahnhöfe der Schweiz sind am vollsten?

Die SBB veröffentlicht für jeden Bahnhof, wie viele Menschen dort im Schnitt pro Tag ein- und aussteigen:
**[Ein- und Aussteigende an Bahnhöfen](https://data.sbb.ch/explore/dataset/passagierfrequenz/)** (auch auf [opendata.swiss](https://opendata.swiss/de/dataset/passagierfrequenz1)).

**Was die Zahlen bedeuten** – bevor du rechnest:
- **DTV** = durchschnittlicher **t**äglicher **V**erkehr (alle Tage des Jahres), **DWV** = durchschnittlicher **W**erktags**v**erkehr (Mo–Fr).
- **Umsteigende zählen doppelt** – einmal beim Aussteigen, einmal beim Einsteigen.
- Nicht alle Bahnunternehmen sind überall enthalten (steht in der Spalte zu den Bahnunternehmen im Datensatz).

### B1 · Live laden (10 min)

Die Datei ist zu groß und zu „lebendig" zum Abtippen – du lädst sie direkt vom SBB-Portal:

1. **Start → Daten transformieren → Neue Quelle → Leere Abfrage → Erweiterter Editor** →
   den Inhalt von [`04_sbb_passagierfrequenz_live.pq`](Loesungen/PowerQuery/04_sbb_passagierfrequenz_live.pq) einfügen → **Fertig**.
2. Bei **Anmeldeinformationen bearbeiten** → **Anonym → Verbinden**. Name der Abfrage: `sbb_bahnhoefe`.
3. Genauso [`02b_dim_kanton.pq`](Loesungen/PowerQuery/02b_dim_kanton.pq) als `dim_kanton` laden.
4. **Schließen & übernehmen** → Modellansicht → `sbb_bahnhoefe[Kanton]` auf `dim_kanton[Kanton]` (n:1).
5. Measures aus [`measures.dax`](Loesungen/DAX/measures.dax), Abschnitt *Teil B*, anlegen:
   `Letztes Jahr`, `Ein- und Aussteigende pro Tag`, `Werktagsfaktor`, `Anzahl Bahnhöfe`.

> ✅ **Kontrollpunkt:** Die Tabelle hat mehrere Tausend Zeilen (mehrere Jahre × alle Bahnhöfe) mit den Spalten
> `Bahnhof`, `Kanton`, `Jahr`, `DTV`, `DWV`, `Breitengrad`, `Längengrad`.
> Die genauen Zahlen hängen vom aktuellen Stand der SBB-Daten ab – deshalb hier kein fester Wert.
> **Plausibilitätsprüfung:** Tabelle `Bahnhof` × `Ein- und Aussteigende pro Tag`, absteigend – ganz oben steht **Zürich HB**.

> 🆘 **Hängst du fest?**
> - **„Zugriff auf die Webinhalte" / Zeitüberschreitung / Proxy-Fehler:** Das Firmennetz sperrt data.sbb.ch. Lade die Datei zu Hause oder im Browser:
>   [Datensatz öffnen](https://data.sbb.ch/explore/dataset/passagierfrequenz/) → **Export → CSV** → speichern → in Power BI
>   **Daten abrufen → Text/CSV**. Danach im Erweiterten Editor nur die Zeile `Quelle = …` durch den neuen Quelle-Schritt ersetzen.
> - **Fehler „Spalte … nicht gefunden":** Die SBB hat eine Spalte umbenannt. Im Schritt `Kopfzeile` nachsehen, wie sie jetzt heißt, und in der Liste `Wunsch` den Anfang anpassen.
> - **Riesige Zahlen bei mehreren Jahren:** DTV ist ein **Tagesdurchschnitt** – den darf man nicht über Jahre addieren. Genau deshalb rechnet das Measure immer nur ein Jahr; mit einem Datenschnitt `Jahr` wählst du, welches.
> - **Kanton „(Leer)":** Ein paar Bahnhöfe liegen an der Grenze oder haben keinen Kanton im Datensatz. Das ist echt – nicht wegfiltern, sondern zeigen und erklären.

> 📚 **Mehr dazu:** [Praxis-Pfad · Modul 5 Aggregation](https://datenwgknowledgekitchen.com/powerbi_praxis_pfad.html#modul-5) ·
> Microsoft Learn: [Aggregate in Berichten](https://learn.microsoft.com/de-de/power-bi/create-reports/service-aggregates) ·
> [Web-Connector](https://learn.microsoft.com/de-de/power-query/connectors/web/web)

### B2 · Die Seite (15 min)

1. **Karte** (Visual *Karte* oder *Azure Maps*): `Breitengrad`, `Längengrad`, Größe = `Ein- und Aussteigende pro Tag`, QuickInfo = `Bahnhof`.
2. **Balkendiagramm** `Bahnhof` × `Ein- und Aussteigende pro Tag` → im Bereich **Filter** bei `Bahnhof`: **Filtertyp Top N → 10** nach dem Measure.
3. **Balkendiagramm** `dim_kanton[Hauptsprache]` × `Ein- und Aussteigende pro Tag`.
4. **Datenschnitt** `sbb_bahnhoefe[Jahr]` (Einzelauswahl).
5. **Tabelle** der Top-10-Bahnhöfe mit `Werktagsfaktor`: Wo ist werktags viel mehr los als am Wochenende (Pendler), wo kaum (Ausflugsziele, Flughafen)?

> ✅ **Kontrollpunkt:** Zürich HB ist in der Karte der größte Punkt und im Top-10-Balken ganz oben.
> Beim Klick auf einen Kanton im Sprach-Balken filtern sich Karte und Top 10 mit.

> 🆘 **Hängst du fest?**
> - **Karte leer oder Punkte im Meer:** Breiten- und Längengrad vertauscht, oder die Spalten sind noch Text. In der Datenansicht Typ prüfen, in der Feldliste **Datenkategorie** auf *Breitengrad* bzw. *Längengrad* setzen.
> - **Karten-Visual fehlt oder ist gesperrt:** In manchen Firmen sind Kartenvisuals deaktiviert (**Datei → Optionen → Sicherheit**). Dann einfach die Top-10-Balken nutzen.

> 📚 **Mehr dazu:** [Einsteiger-Guide · Visualisierung](https://datenwgknowledgekitchen.com/power_bi_einsteiger_guide_v4.html#viz) ·
> [Einsteiger-Guide · Interaktion](https://datenwgknowledgekitchen.com/power_bi_einsteiger_guide_v4.html#inter) ·
> Microsoft Learn: [Visualisierungen](https://learn.microsoft.com/de-de/power-bi/visuals/power-bi-visualizations-overview) ·
> [Visuelle Interaktionen](https://learn.microsoft.com/de-de/power-bi/create-reports/service-reports-visual-interactions)

---

## Teil C · Wie entwickeln sich die Fahrgäste seit 2004?

Eurostat liefert Fahrgastzahlen je Land und Jahr: **[rail_pa_total – Passengers transported](https://ec.europa.eu/eurostat/databrowser/view/rail_pa_total/default/table?lang=en)**.
Über die Schnittstelle kommt die Tabelle im **TSV-Format** – eine echte Kreuztabelle mit einer Spalte je Jahr und
Werten wie `123456 p` (p = vorläufig) oder `:` (fehlt). Genau das richtige Material zum Entpivotieren.

### C1 · Laden und entpivotieren (15 min)

1. **Neue Quelle → Leere Abfrage → Erweiterter Editor** → [`05_eurostat_funktion.pq`](Loesungen/PowerQuery/05_eurostat_funktion.pq) einfügen → Name `fxEurostat`.
   Das ist eine **Funktion**: Sie lädt eine beliebige Eurostat-Tabelle und entpivotiert sie.
2. Noch eine **Leere Abfrage** → [`06_eurostat_fahrgaeste.pq`](Loesungen/PowerQuery/06_eurostat_fahrgaeste.pq) einfügen → Name `fakt_fahrgaeste`. **Anonym** verbinden.
3. Klick in `fakt_fahrgaeste` die **Angewendeten Schritte** der Reihe nach an – so siehst du, was jeder Schritt macht.
   Klick auch in `fxEurostat` auf **Aufrufen** mit `rail_pa_total`: Dort siehst du die Kreuztabelle vor und nach dem Entpivotieren.
4. **Schließen & übernehmen** → Modellansicht → `fakt_fahrgaeste[geo]` auf `dim_land[Code]` (n:1).
5. Measures `Fahrgäste Mio`, `Fahrgäste Vorjahr`, `Δ Fahrgäste %` aus [`measures.dax`](Loesungen/DAX/measures.dax) (Abschnitt *Teil C*).

> ✅ **Kontrollpunkt:** Liniendiagramm `fakt_fahrgaeste[Jahr]` × `Fahrgäste Mio`: Die Linie beginnt 2004 und hat **2020 einen tiefen Einbruch** (Corona).
> Balken `dim_land[Land]` × `Fahrgäste Mio` für das letzte Jahr: **Deutschland** liegt weit vorn.
> Die genauen Werte ändern sich, wenn Eurostat nachliefert – deshalb hier keine feste Zahl.

> 🆘 **Hängst du fest?**
> - **Werte doppelt so hoch wie erwartet:** Die Zeilen `EU27_2020` & Co. sind **Summen** – mit ihnen zählst du Europa zweimal. Das Skript filtert sie mit „Code hat zwei Buchstaben" heraus.
> - **Zwei ganz verschiedene Größenordnungen:** Die Tabelle hat zwei Einheiten, **THS_PAS** (Tausend Fahrgäste) und **MIO_PKM** (Mio. Personenkilometer). Nie mischen – das Skript nimmt nur THS_PAS.
> - **Ein Land heißt „(Leer)":** Das Land steht bei Eurostat, aber nicht in `dim_land` (z. B. **Belgien**, das in der Infografik fehlt). Echte Daten sind selten vollständig – `dim_land.csv` ergänzen oder im Visual ausfiltern.
> - **Firmennetz sperrt ec.europa.eu:** Im [Databrowser](https://ec.europa.eu/eurostat/databrowser/view/rail_pa_total/default/table?lang=en) **Download → CSV** und über **Text/CSV** laden. Die CSV ist schon lang (eine Zeile je Wert) – dann entfällt das Entpivotieren.

> 📚 **Mehr dazu:** Microsoft Learn: [Spalten entpivotieren](https://learn.microsoft.com/de-de/power-query/unpivot-column) ·
> [Zeitintelligenz-Funktionen](https://learn.microsoft.com/de-de/dax/time-intelligence-functions-dax) ·
> Eurostat: [TSV-Format der Schnittstelle](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-faq)

### C2 · Bonus: pro Kopf selbst rechnen (10 min)

Die Funktion `fxEurostat` funktioniert mit **jeder** Eurostat-Tabelle. Hol dir die Bevölkerung
(z. B. Tabelle `tps00001`, Bevölkerung am 1. Januar) mit `fxEurostat("tps00001")`, verknüpfe sie über `geo` und `Jahr`,
und rechne `Fahrgäste ÷ Einwohner`. Kommst du für die Schweiz in die Nähe der 57,9 aus Teil A? Und wie sieht dann
ein **echter Europa-Wert** aus – im Vergleich zum Durchschnitt der Länder (15,45)?

---

## Extra · Von der Kreuztabelle zum Sternschema (Demo, 20 min)

So kommen Daten oft aus Excel: **eine Zeile je Bahnhof, eine Spalte je Monat**, und Stadt, Bundesland und Größenklasse
stehen in jeder Zeile mit dabei. Zum Lesen ist das bequem, zum Rechnen nicht:
[`bahnhoefe_reisende_2025_kreuztabelle.csv`](Daten/1-Rohdaten/bahnhoefe_reisende_2025_kreuztabelle.csv)
(96 Bahnhöfe, Reisende pro Monat 2025 – die Monatswerte sind **simuliert**, die Größenordnung je Bahnhof ist realistisch).

```
https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/1-Rohdaten/bahnhoefe_reisende_2025_kreuztabelle.csv
```

**Woran man sieht, dass die Tabelle nicht normalisiert ist:**
- **„Berlin" steht 22-mal in der Tabelle** – bei 11 Berliner Bahnhöfen je einmal als Stadt und als Bundesland. Ändert sich etwas, musst du es an vielen Stellen ändern.
- **Stadt → Bundesland** hängt nicht vom Bahnhof ab, sondern von der Stadt (Hamburg ist immer Hamburg) – eine versteckte Abhängigkeit.
- **Die Monate sind Spalten:** Ein neuer Monat braucht eine neue Spalte, und „Summe über alle Monate" oder „Filter auf Q1" geht nur umständlich.

**Umbau in Power Query (drei Abfragen):**
1. `roh_bahnhoefe` laden (**Daten abrufen → Web**, Adresse oben), **Laden aktivieren** ausschalten.
2. `fakt_reisende`: **Rechtsklick → Verweis** → Stadt, Bundesland, Größenklasse entfernen → `Bahnhof` markieren →
   **Andere Spalten entpivotieren** → `Attribut` in `Monat` (Typ Datum), `Wert` in `Reisende` (Ganze Zahl).
3. `dim_bahnhof`: **Verweis** → nur Bahnhof, Stadt, Bundesland, Größenklasse behalten → **Duplikate entfernen**.
4. Modellansicht: `fakt_reisende[Bahnhof]` → `dim_bahnhof[Bahnhof]` (n:1). Dazu eine Kalendertabelle an `Monat` – fertig ist der Stern.

> ✅ **Kontrollpunkt:** `fakt_reisende` **1.152 Zeilen** (96 × 12) · Summe `Reisende` **2.906.495.000** ·
> Januar **226.644.366** · Hamburg Hauptbahnhof 2025 **196.005.000** · `dim_bahnhof` **96 Zeilen**, 16 Bundesländer, 77 Städte ·
> Größenklasse A 12 · B 27 · C 57 · stärkstes Bundesland **Berlin** mit 599.695.000.

> 🆘 **Hängst du fest?**
> - **Nur noch 96 Zeilen und eine riesige Zahl:** *Spalten entpivotieren* statt *Andere Spalten entpivotieren* – Schritt löschen, noch einmal.
> - **Fehler in der Spalte `Reisende` (Text wie „Berlin" zwischen den Zahlen):** Stadt, Bundesland und Größenklasse wurden mit entpivotiert. Vorher entfernen – oder alle vier beschreibenden Spalten markieren und dann *Andere Spalten entpivotieren*.
> - **Umlaute kaputt:** Dateiursprung **65001: Unicode (UTF-8)**.
> - ⏭ **Überspringen:** [`07a`](Loesungen/PowerQuery/07a_kreuztabelle_bahnhoefe.pq) · [`07b`](Loesungen/PowerQuery/07b_fakt_reisende.pq) · [`07c`](Loesungen/PowerQuery/07c_dim_bahnhof.pq)

> 📚 **Mehr dazu:** [Einsteiger-Guide · Datenmodell](https://datenwgknowledgekitchen.com/power_bi_einsteiger_guide_v4.html#model) ·
> Microsoft Learn: [Sternschema](https://learn.microsoft.com/de-de/power-bi/guidance/star-schema) ·
> [Spalten entpivotieren](https://learn.microsoft.com/de-de/power-query/unpivot-column) ·
> [Duplikate](https://learn.microsoft.com/de-de/power-query/working-with-duplicates)

---

## Extra · Bordgastronomie: 12 Monatsdateien kombinieren (Demo, 30 min)

Das Bordbistro meldet jeden Monat eine eigene Datei – wie im echten Leben. Im Ordner
[`Daten/1-Rohdaten/bordgastronomie_2025/`](Daten/1-Rohdaten/bordgastronomie_2025/) liegen **12 Dateien**
(`bordgastronomie_2025-01.csv` … `-12.csv`) mit je einer Zeile pro **Fahrt × Bereich × Kategorie**.
**Alle Werte sind simuliert** – Zugnummern und Crew-Kennungen sind ausgedacht, Personen kommen nicht vor.

| Spalte | Inhalt |
|---|---|
| `Datum`, `Wochentag`, `Abfahrt` | Tag und Abfahrtszeit am Startbahnhof |
| `Zugnummer`, `Linie`, `Von`, `Nach` | 5 Linien ab Köln Hbf: München, Berlin, Brüssel, Hamburg, Basel – je 3 Zugpaare am Tag |
| `ICE-Typ`, `Baureihe` | ICE 3neo (BR 408), ICE 4 (BR 412), ICE 3M (BR 406), ICE 1 (BR 401) |
| `Crew`, `Crew-Standort` | Bordgastro-Team (z. B. `BG-KOE-07`) und sein Standort |
| `Bereich` | **Bistro** oder **Restaurant** – ein Restaurant haben nur ICE 1 und ICE 4 |
| `Kategorie` | Getränke · Alkoholische Getränke · Snacks · Mahlzeiten (Snacks nur im Bistro) |
| `Steuersatz` | **Speisen im Bistro 7 %, Speisen im Restaurant 19 %, Getränke immer 19 %** (Stand 2025) |
| `Anzahl Artikel`, `Umsatz netto`, `MwSt`, `Umsatz brutto` | Komma als Dezimalzeichen |

**Laden:**
- **Offline (ZIP entpackt):** **Daten abrufen → Ordner** → Ordner `bordgastronomie_2025` → **Kombinieren und transformieren** →
  Beispieldatei *Erste Datei* → **OK**. Danach Typen mit Gebietsschema **Deutsch (Deutschland)** setzen.
- **Online:** fertiges Skript [`08_bordgastronomie_12_monate.pq`](Loesungen/PowerQuery/08_bordgastronomie_12_monate.pq) als leere Abfrage einfügen.

> ✅ **Kontrollpunkt:** **62.376 Zeilen** · 10.752 Fahrten mit Umsatz (198 ohne – Bistro zu oder Zug ausgefallen) ·
> Umsatz netto **14.311.110,25 €**, brutto **16.325.622,95 €** · Januar netto 1.055.703,46 € · stärkster Monat **August** 1.350.235,35 € ·
> stärkste Linie **Köln – Berlin** 3.496.511,59 € · Bistro 11.076.048,91 € / Restaurant 3.235.061,34 € ·
> 7 %: 5.871.654,82 € / 19 %: 8.439.455,43 € (netto).

> 🆘 **Hängst du fest?**
> - **Nur 5.000 Zeilen:** Du hast eine einzelne Datei statt des Ordners geladen.
> - **Kopfzeile taucht 11-mal als Datenzeile auf:** Beim Kombinieren die Kopfzeile **in der Beispieldatei** höherstufen, nicht danach in der kombinierten Tabelle.
> - **Umsatz × 100 oder Datum als Fehler:** Gebietsschema – Typ ändern **Mithilfe des Gebietsschemas… → Deutsch (Deutschland)**.
> - **Restaurant fehlt bei München und Brüssel:** Kein Fehler – ICE 3neo und ICE 3M haben nur ein Bistro.

> 📚 **Mehr dazu:** [Einsteiger-Guide · Power Query](https://datenwgknowledgekitchen.com/power_bi_einsteiger_guide_v4.html#pq) ·
> Microsoft Learn: [Datentypen](https://learn.microsoft.com/de-de/power-query/data-types) ·
> [Text/CSV](https://learn.microsoft.com/de-de/power-query/connectors/text-csv)

**Ideen für Fragen:** Umsatz pro Fahrt je Linie und ICE-Typ · Alkoholanteil nach Abfahrtszeit und Wochentag ·
Crew-Vergleich (Umsatz pro Fahrt) · Was bringt ein Restaurant? (ICE 4 vs. ICE 3neo) · Steuerlast 7 % vs. 19 % ·
Sternschema: `dim_zug` (Zugnummer, Linie, ICE-Typ, Baureihe), `dim_crew`, Kalender.

---

## Für Trainer:innen

- **Warum dieser Fall:** Bahn-Leute kennen die Fragen und die Stolperfallen der Zahlen (Umsteigende doppelt,
  Tag vs. Werktag, Summen über Länder). Das eignet sich für die Grundfrage *„Was misst diese Zahl eigentlich?"*.
- **Einstieg (5 min):** [Kitchen-Infografik](https://datenwgknowledgekitchen.com/zugfahrten-infografik.html) zeigen, fragen:
  *„Wo liegt Deutschland?"* (Rang 5, 35,1 Fahrten pro Kopf, die Schweiz 1,65-mal so viel).
- **Live-Teile vorher testen:** B und C holen Daten aus dem Internet. Im Schulungsnetz einmal vorab laden.
  Wenn das Netz sperrt, reicht Teil A allein für eine Stunde.
- **Datenstand:** Die Pro-Kopf-Werte sind die Eurostat-Werte 2024 aus der Kitchen-Infografik (eine Nachkommastelle).
  Die Ziele sind ausgedacht. Die Dateien erzeugt [`_Werkzeuge/fall-bahn/daten_erzeugen.py`](../_Werkzeuge/fall-bahn/daten_erzeugen.py).
- **Quellen und Lizenzen:** Eurostat (Weiterverwendung mit Quellenangabe erlaubt), SBB Open Data (offene Nutzung mit Quellenangabe).
  In jedem Bericht die Quelle in die Fußzeile schreiben.
