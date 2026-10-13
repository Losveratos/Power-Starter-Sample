#!/usr/bin/env python3
"""Baut die Download-Pakete für Teilnehmende ohne GitHub-Kenntnisse.

00-Downloads/
  Agenda.pdf, Handout.pdf                           direkt zum Öffnen
  Starter-Training-Tag1.zip                         Übungen als PDF + Daten + Lösung
  Starter-Training-Tag2.zip
  Fall-Weiterbildungs-Monitoring.zip                Anleitung als PDF + Daten + Skripte + Mockup
  Loesung-Weiterbildungs-Monitoring-PowerBI.zip     fertiges Power-BI-Projekt (PBIP)
  Fall-Bahn-Europa.zip                              Anleitung als PDF + Daten + Skripte
  Bordgastronomie-2025-12-Monate.zip                nur die 12 Monatsdateien der Bordgastronomie

PDFs werden aus den Markdown-Dateien des Repos gerendert (Chromium über Playwright),
relative Links zeigen im PDF auf die Dateien auf GitHub. ZIPs haben feste Zeitstempel,
damit sich unveränderte Pakete beim Neubauen nicht ändern.

Aufruf aus dem Repo-Root:
  pip install markdown playwright
  PLAYWRIGHT_CHROMIUM=/pfad/zu/chrome python3 _Werkzeuge/downloads_bauen.py
"""
import os
import re
import tempfile
import zipfile
from pathlib import Path

import markdown
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "00-Downloads"
GH_BLOB = "https://github.com/Losveratos/Power-Starter-24-25-September/blob/main/"
ZIP_TIME = (2025, 9, 24, 8, 0, 0)

CSS = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm; }
body { font-family: 'DejaVu Sans', 'Segoe UI', Arial, sans-serif; font-size: 10pt; line-height: 1.45; color: #0F1E2E; }
h1 { font-size: 20pt; margin: 0 0 6pt; color: #0F1E2E; border-bottom: 3px solid #C25A2D; padding-bottom: 4pt; }
h2 { font-size: 14pt; margin: 16pt 0 6pt; color: #0F1E2E; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; page-break-after: avoid; }
h4 { font-size: 10.5pt; margin: 10pt 0 4pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; font-size: 9pt; page-break-inside: avoid; }
th, td { border: 1px solid #D5DADF; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #EEF1F5; }
code { font-family: 'DejaVu Sans Mono', Consolas, monospace; font-size: 8.5pt; background: #F1F3F5; padding: 0 2pt; border-radius: 2pt; }
pre { background: #F1F3F5; padding: 6pt 8pt; border-radius: 4pt; white-space: pre-wrap; word-break: break-all; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { margin: 6pt 0; padding: 4pt 10pt; border-left: 3px solid #1E8F9E; background: #F3F8F9; }
a { color: #1E6F7B; text-decoration: none; }
img { max-width: 100%; }
hr { border: 0; border-top: 1px solid #D5DADF; margin: 12pt 0; }
.fuss { margin-top: 18pt; font-size: 8pt; color: #6B7280; }
"""


def md_to_html(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8")
    # GitHub erlaubt Listen direkt unter einem Absatz, Python-Markdown braucht eine Leerzeile davor
    lines, out = text.splitlines(), []
    for i, line in enumerate(lines):
        is_item = re.match(r"^\s*([-*]|\d+\.)\s", line)
        prev = out[-1] if out else ""
        if is_item and prev.strip() and not re.match(r"^\s*([-*]|\d+\.)\s", prev) and not prev.startswith((" ", "\t")):
            out.append("")
        out.append(line)
    text = "\n".join(out)
    body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    rel_dir = md_path.parent.relative_to(ROOT)

    def fix(m):
        attr, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|mailto:|#)", url):
            return m.group(0)
        target = (ROOT / rel_dir / url.split("#")[0]).resolve()
        if attr == "src":                                   # Bilder lokal einbetten
            return f'{attr}="{target.as_uri()}"'
        try:
            rel = target.relative_to(ROOT).as_posix()
        except ValueError:
            return m.group(0)
        anchor = "#" + url.split("#", 1)[1] if "#" in url else ""
        return f'{attr}="{GH_BLOB}{rel}{anchor}"'

    body = re.sub(r'(href|src)="([^"]+)"', fix, body)
    return (f"<!doctype html><html lang='de'><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"{body}<p class='fuss'>Power BI Starter-Training · github.com/Losveratos/Power-Starter-24-25-September</p>"
            "</body></html>")


def render_pdfs(jobs):
    launch = {"executable_path": os.environ["PLAYWRIGHT_CHROMIUM"]} if os.environ.get("PLAYWRIGHT_CHROMIUM") else {}
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.chromium.launch(**launch)
        page = browser.new_page()
        for md, pdf in jobs:
            html = Path(tmp) / (pdf.stem + ".html")
            html.write_text(md_to_html(md), encoding="utf-8")
            page.goto(html.as_uri())
            page.wait_for_load_state("networkidle")
            page.pdf(path=str(pdf), format="A4", print_background=True,
                     display_header_footer=True, header_template="<span></span>",
                     footer_template="<div style='font-size:7pt;color:#6B7280;width:100%;text-align:center'>"
                                     "<span class='pageNumber'></span> / <span class='totalPages'></span></div>",
                     margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"})
            print("  PDF", pdf.name)
        browser.close()


def write_zip(name, entries):
    """entries: Liste von (Pfad im ZIP, Quelle: Path | str-Inhalt)."""
    path = OUT / name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, src in sorted(entries, key=lambda e: e[0]):
            data = src.read_bytes() if isinstance(src, Path) else src.encode("utf-8")
            info = zipfile.ZipInfo(arc, date_time=ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, data)
    print(f"  ZIP {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB, {len(entries)} Dateien)")


def tree(src: Path, prefix: str, skip=()):
    return [(f"{prefix}/{f.relative_to(src).as_posix()}", f) for f in sorted(src.rglob("*"))
            if f.is_file() and not any(s in f.parts for s in skip)]


LIESMICH_TAG = """Power BI Starter-Training · {tag}
=====================================

1. Diese ZIP-Datei entpacken: Rechtsklick → „Alle extrahieren…" → „Extrahieren".
   (Direkt aus der ZIP heraus öffnen klappt oft nicht.)
2. „{pdf}" öffnen – dort stehen alle Übungen Schritt für Schritt.
3. Die Daten lädst du in Power BI am einfachsten direkt aus dem Internet (Adresse steht in der Übung).
   Klappt das nicht (Firmen-Proxy), nimm die Dateien aus dem Ordner „Daten":
   Power BI → Start → Daten abrufen → Text/CSV (bzw. Excel-Arbeitsmappe).
4. Steckst du fest? Im Ordner „Loesungen" liegt der fertige Power-Query- und DAX-Code
   (mit dem Windows-Editor öffnen, alles kopieren, in Power BI einfügen).

Alles online: https://github.com/Losveratos/Power-Starter-24-25-September
"""


def main():
    OUT.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    case = ROOT / "03-Fall-Weiterbildung"
    bahn = ROOT / "05-Fall-Bahn"
    pdf = {
        "agenda": OUT / "Agenda.pdf",
        "handout": OUT / "Handout.pdf",
        "tag1": tmp / "Uebungen-Tag1.pdf",
        "tag2": tmp / "Uebungen-Tag2.pdf",
        "fall": tmp / "Anleitung-Weiterbildungs-Monitoring.pdf",
        "pbip": tmp / "LIESMICH-PowerBI.pdf",
        "bahn": tmp / "Anleitung-Bahn-Europa.pdf",
    }
    render_pdfs([(ROOT / "04-Material/Agenda.md", pdf["agenda"]), (ROOT / "04-Material/Handout.md", pdf["handout"]),
                 (ROOT / "01-Tag-1/README.md", pdf["tag1"]), (ROOT / "02-Tag-2/README.md", pdf["tag2"]),
                 (case / "README.md", pdf["fall"]), (case / "PowerBI-Loesung/README.md", pdf["pbip"]),
                 (bahn / "README.md", pdf["bahn"])])

    write_zip("Starter-Training-Tag1.zip", [
        ("LIESMICH.txt", LIESMICH_TAG.format(tag="Tag 1", pdf="Uebungen-Tag1.pdf")),
        ("Uebungen-Tag1.pdf", pdf["tag1"]), ("Handout.pdf", pdf["handout"]), ("Agenda.pdf", pdf["agenda"]),
        ("Daten/verkaeufe_2025_roh.csv", ROOT / "01-Tag-1/Daten/verkaeufe_2025_roh.csv"),
        *[(f"Loesungen/{f.stem}.txt", f) for f in sorted((ROOT / "01-Tag-1/Loesungen").iterdir())],
    ])
    write_zip("Starter-Training-Tag2.zip", [
        ("LIESMICH.txt", LIESMICH_TAG.format(tag="Tag 2", pdf="Uebungen-Tag2.pdf")),
        ("Uebungen-Tag2.pdf", pdf["tag2"]), ("Handout.pdf", pdf["handout"]), ("Agenda.pdf", pdf["agenda"]),
        *[(f"Daten/{f.name}", f) for f in sorted((ROOT / "02-Tag-2/Daten").iterdir())],
        *[(f"Loesungen/{f.stem}.txt", f) for f in sorted((ROOT / "02-Tag-2/Loesungen").iterdir())],
    ])
    write_zip("Fall-Weiterbildungs-Monitoring.zip", [
        ("LIESMICH.txt", LIESMICH_TAG.format(tag="Fall Weiterbildungs-Monitoring",
                                             pdf="Anleitung-Weiterbildungs-Monitoring.pdf")),
        ("Anleitung-Weiterbildungs-Monitoring.pdf", pdf["fall"]),
        ("Ziel-Seite-Mockup.png", case / "Mockup/page-1-uberblick.png"),
        ("Mockup/weiterbildungs-monitoring.mockup.json", case / "Mockup/weiterbildungs-monitoring.mockup.json"),
        *[(f"Daten/{f.relative_to(case / 'Daten').as_posix()}", f) for f in sorted((case / "Daten").rglob("*")) if f.is_file()],
        *[(f"Loesungen/{f.stem}.txt", f) for f in sorted((case / "Loesungen").rglob("*")) if f.is_file()],
    ])
    write_zip("Loesung-Weiterbildungs-Monitoring-PowerBI.zip", [
        ("LIESMICH.txt", """Fertige Lösung · Weiterbildungs-Monitoring (Power BI)
===================================================

1. ZIP entpacken: Rechtsklick → „Alle extrahieren…" → „Extrahieren".
   WICHTIG: nicht aus der ZIP heraus öffnen – Power BI braucht alle Ordner.
2. Im entpackten Ordner „Weiterbildungs-Monitoring" die Datei
   „Weiterbildungs-Monitoring.pbip" doppelklicken (Power BI Desktop muss installiert sein).
3. In Power BI: Start → Aktualisieren. Bei der Frage nach Anmeldedaten „Anonym" → „Verbinden".
4. Wer eine normale .pbix-Datei möchte: Datei → Speichern unter → Power BI-Datei (.pbix).

Details: LIESMICH-PowerBI.pdf
"""),
        ("LIESMICH-PowerBI.pdf", pdf["pbip"]),
        *tree(case / "PowerBI-Loesung", "Weiterbildungs-Monitoring",
              skip=(".pbi",)),
    ])
    write_zip("Fall-Bahn-Europa.zip", [
        ("LIESMICH.txt", LIESMICH_TAG.format(tag="Fall Bahn in Europa", pdf="Anleitung-Bahn-Europa.pdf")),
        ("Anleitung-Bahn-Europa.pdf", pdf["bahn"]),
        *[(f"Daten/{f.relative_to(bahn / 'Daten').as_posix()}", f) for f in sorted((bahn / "Daten").rglob("*")) if f.is_file()],
        *[(f"Loesungen/{f.stem}.txt", f) for f in sorted((bahn / "Loesungen").rglob("*")) if f.is_file()],
    ])
    bordgastro = bahn / "Daten/1-Rohdaten/bordgastronomie_2025"
    write_zip("Bordgastronomie-2025-12-Monate.zip",
              [(f"bordgastronomie_2025/{f.name}", f) for f in sorted(bordgastro.glob("*.csv"))])


if __name__ == "__main__":
    main()
