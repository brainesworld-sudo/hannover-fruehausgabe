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
from urllib.parse import quote_plus
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUSGABEN = ROOT / "ausgaben"
SITE_URL = "https://fruehausgabe.hilmerjahnke.de"
# Die Frühausgabe erschien vorher schon 32-mal als Claude-Seite; die Web-Zählung setzt dort fort.
AUSGABE_OFFSET = 32

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]

RESSORTS = {
    "hannover":    ("Hannover & Region", "#1f6f78", "Vor der Haustür"),
    "deutschland": ("Deutschland",       "#b4432b", "Was das Land bewegt"),
    "welt":        ("Die Welt",          "#4b4fa6", "Was draußen passiert"),
    "sport":       ("Sport",             "#7a4fa0", "Hannover zuerst, dann der Rest"),
    "netz":        ("Was das Netz sucht", "#a8781f", "Google Trends Deutschland"),
}

BEWERTUNG = {
    "gesichert": ("Gesichert", "v3"),
    "plausibel": ("Plausibel, Details offen", "v2"),
    "vorsicht":  ("Mit Vorsicht genießen", "v1"),
}


def balken(key):
    label, cls = BEWERTUNG.get(key, BEWERTUNG["plausibel"])
    return f'<span class="val {cls}"><span class="bars"><i></i><i></i><i></i></span>{label}</span>'


def karte(ort):
    """◎-Link zu Google Maps; ort ist ein Suchbegriff oder {"name": ..., "suche": ...}."""
    if isinstance(ort, dict):
        name = ort.get("name") or ort.get("suche")
        suche = ort.get("suche") or ort.get("name")
        titel = f"Karte: {txt(name)}"
    else:
        name = suche = ort
        titel = "Karte"
    if not suche:
        return ""
    url = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(str(suche))
    return f'<a class="geo" href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{titel}</a>'


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
:root{--bg:#f5f2ea;--card:#fffdf8;--ink:#1f1d1a;--muted:#6b655c;--line:#e2dccf;
--ok:#2e7d4f;--mid:#b7861a;--bad:#b03a2e;--corebg:#1f2a37;--coreink:#f5f2ea;
--warnbg:#fbede9;--warnline:#e4b3a8;--startbg:#e8f2ef;--startline:#a9cfc5;--hann:#0e6e6b;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171614;--card:#211f1c;--ink:#ede8de;
--muted:#a39c90;--line:#35322d;--ok:#5bbe83;--mid:#d9a83a;--bad:#e07a6c;--corebg:#2a3544;--coreink:#ede8de;
--warnbg:#2e1e1b;--warnline:#5c352e;--startbg:#16292a;--startline:#2c4e4b;--hann:#4fb3ad;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#171614;--card:#211f1c;--ink:#ede8de;--muted:#a39c90;--line:#35322d;--ok:#5bbe83;
--mid:#d9a83a;--bad:#e07a6c;--corebg:#2a3544;--coreink:#ede8de;--warnbg:#2e1e1b;--warnline:#5c352e;
--startbg:#16292a;--startline:#2c4e4b;--hann:#4fb3ad;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 "Iowan Old Style","Palatino Linotype",Georgia,serif}
.wrap{max-width:980px;margin:0 auto;padding:22px 16px 48px;display:flex;flex-direction:column;gap:26px}
a{color:inherit;text-underline-offset:2px}
.label{font:600 11px "Helvetica Neue",Helvetica,Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
header.top{border-bottom:3px double var(--ink);padding-bottom:12px;display:flex;flex-direction:column;gap:6px}
header.top .row{display:flex;justify-content:space-between;flex-wrap:wrap;gap:6px}
h1{font-size:clamp(34px,7vw,58px);line-height:1;margin:0;font-weight:700;letter-spacing:-.01em}
h1 i{font-weight:400}
header.top p{margin:0;color:var(--muted);font-size:15px}
header.top nav a{font:13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);margin-right:14px}
.notice{font:12.5px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);margin:-12px 0 0}
.core{background:var(--corebg);color:var(--coreink);border-radius:6px;padding:20px 22px}
.core .label{color:var(--coreink);opacity:.75}
.core ol{margin:10px 0 0;padding-left:1.2em;display:flex;flex-direction:column;gap:6px}
.core li::marker{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;font-weight:700}
.legend{display:flex;flex-wrap:wrap;gap:8px 18px;font:13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);align-items:center}
section.res{--c:#666;display:flex;flex-direction:column;gap:14px}
.res-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.pill{background:var(--c);color:#fff;font:700 13px "Helvetica Neue",Helvetica,Arial,sans-serif;border-radius:999px;padding:3px 11px}
.res-head h2{margin:0;font-size:26px;line-height:1.2}
.res-head .sub{font:13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media (max-width:640px){.grid{grid-template-columns:1fr}}
article{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:4px;padding:14px 16px;display:flex;flex-direction:column;gap:8px;min-width:0}
article h3{margin:0;font-size:19px;line-height:1.3}
article p{margin:0}
.meta{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:center;font:12px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted)}
.val{display:inline-flex;align-items:center;gap:6px;font-weight:700}
.bars{display:inline-flex;gap:2px}
.bars i{width:9px;height:9px;border-radius:2px;background:var(--line)}
.v3 i{background:var(--ok)}.v2 i:nth-child(-n+2){background:var(--mid)}.v1 i:first-child{background:var(--bad)}
.v3{color:var(--ok)}.v2{color:var(--mid)}.v1{color:var(--bad)}
.geo{font:700 12px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--c);text-decoration:none;white-space:nowrap}
.geo::before{content:"◎ "}
.geo:hover{text-decoration:underline}
.kurz{margin:0;padding-left:1.1em;display:flex;flex-direction:column;gap:6px}
details{border-top:1px dashed var(--line);padding-top:8px}
summary{cursor:pointer;font:700 13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--c);list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"▸ "}
details[open] summary::before{content:"▾ "}
.long{display:flex;flex-direction:column;gap:10px;margin-top:10px;font-size:16px}
.long p{margin:0}
.why{font:13px/1.45 "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted)}
.src{font:12px/1.5 "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);overflow-wrap:anywhere}
.src a{color:var(--muted)}
.hint{font:13px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);margin:0}
.trends{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:10px}
.tr{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:10px 12px;display:flex;flex-direction:column;gap:3px;min-width:0}
.tr b{font-size:16px;overflow-wrap:anywhere}
.tr span{font:12px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);font-variant-numeric:tabular-nums}
.warn{background:var(--warnbg);border:1px solid var(--warnline);border-radius:6px;padding:18px 20px}
.warn .label{color:var(--bad)}
.warn ul{margin:10px 0 0;padding-left:1.1em;display:flex;flex-direction:column;gap:6px}
.start{background:var(--startbg);border:1px solid var(--startline);border-radius:6px;padding:18px 20px;display:flex;flex-direction:column;gap:12px}
.start .label{color:var(--hann)}
.steps{display:flex;flex-wrap:wrap;gap:10px}
.step{flex:1 1 200px;background:var(--card);border:1px solid var(--startline);border-radius:4px;padding:10px 12px;display:flex;flex-direction:column;gap:4px;min-width:0}
.step .when{font:700 12px "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--hann);letter-spacing:.04em;text-transform:uppercase}
.start ul{margin:0;padding-left:1.1em;display:flex;flex-direction:column;gap:6px}
footer{border-top:1px solid var(--line);padding-top:12px;font:12.5px/1.6 "Helvetica Neue",Helvetica,Arial,sans-serif;color:var(--muted);text-align:center}
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


def kopf(d: date, nummer: int, ist_aktuell: bool, stand: str = ""):
    zusatz = "" if ist_aktuell else '<a href="/">zur aktuellen Ausgabe</a>'
    stand_html = f'<span class="label">{txt(stand)}</span>' if stand else ""
    return f"""<header class="top">
<div class="row"><span class="label">{datumszeile(d)} · Ausgabe {nummer}</span>{stand_html}</div>
<h1>Hannover <i>Frühausgabe</i></h1>
<p>Die Morgenzeitung aus der Region, aus Deutschland und der Welt. Jede Meldung mit Quelle und Glaubwürdigkeits-Check.</p>
<nav><a href="/archiv/">Archiv</a>{zusatz}</nav>
</header>
<p class="notice">Automatisch erstellt mit KI, ohne redaktionelle Prüfung.</p>
"""


def liste(items):
    return "".join(f"<li>{txt(i)}</li>" for i in items or [])


def quellen_html(m):
    q = [f'<a href="{safe_url(x.get("url"))}" rel="noopener" target="_blank">{txt(x.get("name") or "Quelle")}</a>'
         for x in m.get("quellen", []) if safe_url(x.get("url"))]
    return " · ".join(q)


def meldung(m):
    bew = m.get("bewertung", "plausibel")
    orte = "".join(karte(o) for o in (m.get("orte") or []))
    namen = ", ".join(str(x.get("name")) for x in m.get("quellen", []) if x.get("name"))[:90]
    meta = f'<div class="meta">{balken(bew)}' + (f"<span>Quelle: {txt(namen)}</span>" if namen else "") + f"{orte}</div>"
    kurz = f"<p>{txt(m.get('kurz'))}</p>" if m.get("kurz") else ""
    punkte = f'<ul class="kurz">{liste(m["liste"])}</ul>' if m.get("liste") else ""
    lang = "".join(f"<p>{txt(p)}</p>" for p in m.get("lang", []))
    why = f'<p class="why"><b>Einschätzung:</b> {txt(m.get("einschaetzung"))}</p>' if m.get("einschaetzung") else ""
    q = quellen_html(m)
    src = f'<p class="src">Quellen: {q}</p>' if q else ""
    if lang or why:
        mehr = f'<details><summary>Ganzen Artikel lesen</summary><div class="long">{lang}{why}{src}</div></details>'
    elif src:
        mehr = f'<details><summary>Quellen</summary><div class="long">{src}</div></details>'
    else:
        mehr = ""
    return f"<article>\n<h3>{txt(m.get('titel'))}</h3>\n{kurz}{punkte}\n{meta}\n{mehr}\n</article>"


def trends_html(trends):
    kacheln = "".join(
        f'<div class="tr"><b>{txt(t.get("begriff"))}</b><span>{txt(t.get("volumen"))}'
        + (f' · {txt(t.get("anlass"))}' if t.get("anlass") else "") + "</span></div>"
        for t in trends or [] if t.get("begriff"))
    return f'<div class="trends">{kacheln}</div>' if kacheln else ""


def woche_html(woche):
    if not woche:
        return ""
    if all(isinstance(w, dict) for w in woche):
        kacheln = "".join(
            f'<div class="step"><span class="when">{txt(w.get("wann"))}</span><b>{txt(w.get("titel"))}</b>'
            f'<span>{txt(w.get("text"))}</span></div>' for w in woche)
        inhalt = f'<div class="steps">{kacheln}</div>'
    else:
        inhalt = f"<ul>{liste(woche)}</ul>"
    return f'<div class="start"><div class="label">Diese Woche im Blick</div>{inhalt}</div>'


def ausgabe_html(data, d, nummer, ist_aktuell):
    teile = [kopf(d, nummer, ist_aktuell, data.get("stand", ""))]
    if data.get("kurz"):
        teile.append(f'<div class="core"><div class="label">Das Wichtigste in 90 Sekunden</div><ol>{liste(data["kurz"])}</ol></div>')
    teile.append('<div class="legend"><span class="label">Glaubwürdigkeit</span>'
                 + balken("gesichert") + balken("plausibel") + balken("vorsicht") + "</div>")
    for r in data.get("ressorts", []):
        rid = r.get("id")
        if rid not in RESSORTS:
            continue
        name, farbe, sub = RESSORTS[rid]
        sub = r.get("untertitel") or sub
        nr = list(RESSORTS).index(rid) + 1
        hinweis = f'<p class="hint">{txt(r["hinweis"])}</p>' if r.get("hinweis") else ""
        karten = "".join(meldung(m) for m in r.get("meldungen", []))
        grid = f'<div class="grid">{karten}</div>' if karten else ""
        teile.append(f"""<section class="res" style="--c:{farbe}">
<div class="res-head"><span class="pill">{nr}</span><h2>{name}</h2><span class="sub">{txt(sub)}</span></div>
{trends_html(r.get("trends"))}{grid}{hinweis}
</section>""")
    if data.get("faktencheck"):
        teile.append(f'<div class="warn"><div class="label">Faktencheck: Hier genau hinschauen</div><ul>{liste(data["faktencheck"])}</ul></div>')
    teile.append(woche_html(data.get("woche")))
    return "\n".join(teile)


def beschreibung(data, d):
    erste = re.sub(r"<[^>]+>", "", str((data.get("kurz") or [""])[0]))
    return (f"Hannover Frühausgabe vom {datumszeile(d)}. " + erste)[:300]


def main():
    dateien = sorted(AUSGABEN.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json"))
    if not dateien:
        sys.exit("Keine Ausgaben gefunden.")
    eintraege = []
    for nummer, f in enumerate(dateien, start=AUSGABE_OFFSET + 1):
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
        f'<li><a href="/{e[0].isoformat()}/">{datumszeile(e[0])}</a> · Ausgabe {e[1]}</li>'
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
