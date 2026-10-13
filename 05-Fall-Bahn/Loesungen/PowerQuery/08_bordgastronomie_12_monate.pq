// Extra · Bordgastronomie: 12 Monatsdateien in einem Rutsch laden und untereinanderhängen
// Abfrage umbenennen in: fakt_bordgastronomie
// ✅ 62.376 Zeilen · Umsatz netto 14.311.110,25 € · Umsatz brutto 16.325.622,95 €
//
// Offline-Variante: ZIP entpacken → Daten abrufen → Ordner → Ordner „bordgastronomie_2025" → Kombinieren und transformieren.
// Hier die Online-Variante: Die 12 Adressen werden aus den Monatsnummern gebaut.
let
    Basis = "https://raw.githubusercontent.com/Losveratos/Power-Starter-24-25-September/main/05-Fall-Bahn/Daten/1-Rohdaten/bordgastronomie_2025/",
    Monate = List.Transform({1..12}, each "bordgastronomie_2025-" & Text.PadStart(Text.From(_), 2, "0") & ".csv"),
    LadeMonat = (datei as text) as table =>
        Table.PromoteHeaders(
            Csv.Document(Web.Contents(Basis & datei), [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
            [PromoteAllScalars = true]),
    Alle = Table.Combine(List.Transform(Monate, LadeMonat)),
    // Komma als Dezimalzeichen und TT.MM.JJJJ → Gebietsschema Deutsch
    Typen = Table.TransformColumnTypes(Alle, {
        {"Datum", type date}, {"Abfahrt", type time}, {"Anzahl Artikel", Int64.Type},
        {"Umsatz netto", Currency.Type}, {"MwSt", Currency.Type}, {"Umsatz brutto", Currency.Type}}, "de-DE"),
    // „19 %" → 0,19 als Zahl, damit man damit rechnen kann
    Satz = Table.TransformColumns(Typen, {{"Steuersatz", each Number.From(Text.BeforeDelimiter(_, " ")) / 100, type number}})
in
    Satz
