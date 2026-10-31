#!/usr/bin/env python3
"""Hannover Frühausgabe – baut die Website aus den Ausgaben-Dateien.

Jede Ausgabe liegt als JSON in ausgaben/JJJJ-MM-TT.json (Aufbau: siehe AUFBAU.md).
Aufruf:  python3 render.py
Erzeugt: index.html (neueste Ausgabe), JJJJ-MM-TT/index.html (Archiv je Tag),
         archiv/index.html (Übersicht). Nur <b>…</b> ist in Texten erlaubt,
         alles andere wird maskiert.
"""
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUSGABEN = ROOT / "ausgaben"
SITE_URL = "https://fruehausgabe.hilmerjahnke.de"

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

RESSORTS = {
    "hannover":    ("Hannover & Region", "#1f6f78", "#5fb3bc"),
    "deutschland": ("Deutschland",       "#b4432b", "#e0826b"),
    "welt":        ("Welt",              "#4b4fa6", "#9095e0"),
    "sport":       ("Sport",             "#7a4fa0", "#b48fd6"),
    "netz":        ("Was das Netz sucht", "#a8781f", "#e0b25c"),
}

BEWERTUNG = {
    "gesichert": ("Gesichert", "ok"),
    "plausibel": ("Plausibel, Details offen", "mid"),
    "vorsicht":  ("Mit Vorsicht genießen", "warn"),
}


def txt(s):
    """Maskiert alles, lässt nur <b>…</b> stehen."""
    s = html.escape(str(s or ""), quote=True)
    return re.sub(r"&lt;(/?)b&gt;", r"<\1b>", s)


def safe_url(u):
    u = str(u or "").strip()
    return html.escape(u, quote=True) if re.match(r"^https?://", u) else ""


def datumszeile(d: date):
    return f"{WOCHENTAGE[d.weekday()]}, {d.day}. {MONATE[d.month - 1]} {d.year}"


CSS = """
:root{--bg:#f7f3ec;--card:#fffdf8;--ink:#1f1b16;--muted:#6b6258;--line:#e6ddcf;
--ok:#2f7d4f;--mid:#9a6b12;--warn:#b4432b;--box:#efe8db;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171513;--card:#211e1b;
--ink:#efe9df;--muted:#a89e91;--line:#36312b;--ok:#6cc08f;--mid:#e0b25c;--warn:#ec8a72;--box:#2a2622;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#171513;--card:#211e1b;--ink:#efe9df;--muted:#a89e91;--line:#36312b;
--ok:#6cc08f;--mid:#e0b25c;--warn:#ec8a72;--box:#2a2622;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 "Iowan Old Style",Georgia,serif}
.wrap{max-width:980px;margin:0 auto;padding:28px 16px 48px}
.sans{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}
a{color:inherit}
header.top{border-bottom:3px double var(--ink);padding-bottom:14px;margin-bottom:22px;text-align:center}
.eyebrow{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(34px,8vw,58px);line-height:1.05;margin:6px 0 4px;letter-spacing:-.01em}
.dateline{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:13px;color:var(--muted)}
nav.mini{margin-top:10px;font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:13px}
nav.mini a{margin:0 8px;color:var(--muted)}
.notice{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:12.5px;color:var(--muted);
background:var(--box);border-radius:8px;padding:8px 12px;margin:0 0 22px;text-align:center}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:0 0 26px}
.box h2{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-size:12px;letter-spacing:.14em;text-transform:uppercase;margin:0 0 8px}
.box ul{margin:0;padding-left:20px}.box li{margin:4px 0}
.box.key{border-left:5px solid var(--ink)}
.box.check{border-left:5px solid var(--warn)}
.box.week{border-left:5px solid var(--ok)}
section.res{--c:#666;margin:0 0 30px}
.res-head{display:flex;align-items:center;gap:10px;margin:0 0 12px}
.pill{background:var(--c);color:#fff;font:700 12px/1 "Helvetica Neue",Helvetica,Arial,sans-serif;
border-radius:999px;padding:6px 10px;letter-spacing:.06em}
.res-head h2{margin:0;font-size:22px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media (max-width:640px){.grid{grid-template-columns:1fr}}
article{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:10px;padding:14px 16px}
article h3{margin:0 0 6px;font-size:18.5px;line-height:1.3}
article p{margin:0 0 8px}
.rate{display:inline-block;font:600 11.5px/1 "Helvetica Neue",Helvetica,Arial,sans-serif;border-radius:999px;
padding:5px 9px;border:1px solid currentColor;margin:2px 0 6px}
.rate.ok{color:var(--ok)}.rate.mid{color:var(--mid)}.rate.warn{color:var(--warn)}
details{border-top:1px dashed var(--line);margin-top:6px;padding-top:6px}
summary{cursor:pointer;font:600 13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--c);padding:6px 0;list-style-position:inside}
.why{font-size:15px;color:var(--muted);background:var(--box);border-radius:8px;padding:8px 10px;margin:8px 0}
.src{font:13px/1.5 "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted)}
.src a{color:var(--muted)}
.hint{font:13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);margin:-4px 0 12px}
footer{border-top:1px solid var(--line);margin-top:34px;padding-top:14px;font:13px/1.6 "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);text-align:center}
footer a{color:var(--muted)}
.archive li{margin:6px 0}
"""


def page(title, body, canonical, description):
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(description, quote=True)}">
<meta property="og:type" content="article">
<meta name="theme-color" content="#f7f3ec">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
{body}
<footer>
Automatisch erstellt mit KI, ohne redaktionelle Prüfung. Alle Meldungen in eigenen Worten zusammengefasst, Quellen jeweils verlinkt.<br>
<a href="/">Aktuelle Ausgabe</a> · <a href="/archiv/">Archiv</a> · <a href="/impressum.html">Impressum</a> · <a href="https://hilmerjahnke.de">hilmerjahnke.de</a>
</footer>
</div>
</body>
</html>
"""


def kopf(d: date, nummer: int, ist_aktuell: bool):
    zusatz = "" if ist_aktuell else ' · <a href="/">zur aktuellen Ausgabe</a>'
    return f"""<header class="top">
<div class="eyebrow">Hannover · Deutschland · Welt · Sport</div>
<h1>Hannover Frühausgabe</h1>
<div class="dateline">{datumszeile(d)} · Ausgabe Nr. {nummer}</div>
<nav class="mini"><a href="/archiv/">Archiv</a>{zusatz}</nav>
</header>
<div class="notice">Automatisch erstellt mit KI, ohne redaktionelle Prüfung. Jede Meldung trägt eine Glaubwürdigkeits-Einschätzung und ihre Quellen.</div>
"""


def liste(items):
    return "".join(f"<li>{txt(i)}</li>" for i in items or [])


def meldung(m):
    label, cls = BEWERTUNG.get(m.get("bewertung", "plausibel"), BEWERTUNG["plausibel"])
    lang = "".join(f"<p>{txt(p)}</p>" for p in m.get("lang", []))
    quellen = [f'<a href="{safe_url(q.get("url"))}" rel="noopener" target="_blank">{txt(q.get("name") or "Quelle")}</a>'
               for q in m.get("quellen", []) if safe_url(q.get("url"))]
    src = f'<div class="src">Quellen: {" · ".join(quellen)}</div>' if quellen else ""
    why = f'<div class="why"><b>Warum „{label}“:</b> {txt(m.get("einschaetzung"))}</div>' if m.get("einschaetzung") else ""
    mehr = f"<details><summary>Ganzen Artikel lesen</summary>{lang}{why}{src}</details>" if (lang or why or src) else ""
    return f"""<article>
<h3>{txt(m.get("titel"))}</h3>
<span class="rate {cls}">{label}</span>
<p>{txt(m.get("kurz"))}</p>
{mehr}
</article>"""


def ausgabe_html(data, d, nummer, ist_aktuell):
    teile = [kopf(d, nummer, ist_aktuell)]
    if data.get("kurz"):
        teile.append(f'<div class="box key"><h2>Das Wichtigste in 90 Sekunden</h2><ul>{liste(data["kurz"])}</ul></div>')
    for r in data.get("ressorts", []):
        rid = r.get("id")
        if rid not in RESSORTS:
            continue
        name, farbe, _ = RESSORTS[rid]
        nr = list(RESSORTS).index(rid) + 1
        hinweis = f'<p class="hint">{txt(r["hinweis"])}</p>' if r.get("hinweis") else ""
        karten = "".join(meldung(m) for m in r.get("meldungen", []))
        teile.append(f"""<section class="res" style="--c:{farbe}">
<div class="res-head"><span class="pill">{nr}</span><h2>{name}</h2></div>
{hinweis}<div class="grid">{karten}</div>
</section>""")
    if data.get("faktencheck"):
        teile.append(f'<div class="box check"><h2>Faktencheck: Hier genau hinschauen</h2><ul>{liste(data["faktencheck"])}</ul></div>')
    if data.get("woche"):
        teile.append(f'<div class="box week"><h2>Diese Woche im Blick</h2><ul>{liste(data["woche"])}</ul></div>')
    return "\n".join(teile)


def beschreibung(data, d):
    erste = re.sub(r"<[^>]+>", "", str((data.get("kurz") or [""])[0]))
    return (f"Hannover Frühausgabe vom {datumszeile(d)}. " + erste)[:300]


def main():
    dateien = sorted(AUSGABEN.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
    if not dateien:
        sys.exit("Keine Ausgaben gefunden.")
    eintraege = []
    for nummer, f in enumerate(dateien, start=1):
        data = json.loads(f.read_text(encoding="utf-8"))
        d = date.fromisoformat(f.stem)
        eintraege.append((d, nummer, data))
        ziel = ROOT / f.stem / "index.html"
        ziel.parent.mkdir(exist_ok=True)
        ziel.write_text(page(f"Hannover Frühausgabe – {datumszeile(d)}",
                             ausgabe_html(data, d, nummer, False),
                             f"{SITE_URL}/{f.stem}/", beschreibung(data, d)), encoding="utf-8")

    d, nummer, data = eintraege[-1]
    (ROOT / "index.html").write_text(page("Hannover Frühausgabe",
                                          ausgabe_html(data, d, nummer, True),
                                          f"{SITE_URL}/", beschreibung(data, d)), encoding="utf-8")

    zeilen = "".join(
        f'<li><a href="/{e[0].isoformat()}/">{datumszeile(e[0])}</a> · Ausgabe Nr. {e[1]}</li>'
        for e in reversed(eintraege))
    archiv = f"""<header class="top">
<div class="eyebrow">Alle bisherigen Ausgaben</div>
<h1>Archiv</h1>
<nav class="mini"><a href="/">zur aktuellen Ausgabe</a></nav>
</header>
<div class="box"><ul class="archive">{zeilen}</ul></div>"""
    (ROOT / "archiv").mkdir(exist_ok=True)
    (ROOT / "archiv" / "index.html").write_text(
        page("Archiv – Hannover Frühausgabe", archiv, f"{SITE_URL}/archiv/",
             "Alle bisherigen Ausgaben der Hannover Frühausgabe."), encoding="utf-8")
    # Sitemap und robots.txt für Suchmaschinen
    urls = [(f"{SITE_URL}/", d.isoformat(), "daily", "1.0"),
            (f"{SITE_URL}/archiv/", d.isoformat(), "daily", "0.6")]
    urls += [(f"{SITE_URL}/{e[0].isoformat()}/", e[0].isoformat(), "never", "0.5")
             for e in reversed(eintraege)]
    eintraege_xml = "".join(
        f"  <url><loc>{u}</loc><lastmod>{m}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority></url>\n"
        for u, m, c, p in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{eintraege_xml}</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: /ausgaben/\n\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8")

    print(f"{len(eintraege)} Ausgabe(n) gebaut, neueste: {d.isoformat()}")


if __name__ == "__main__":
    main()
