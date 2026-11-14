#!/usr/bin/env python3
"""Baut das Radar-Reel (1080x1920, MP4, stumm) und ein Titelbild zum Tipp des Tages.

Aufruf:  python3 werkzeuge/radar_reel.py post.json reel_JJJJ-MM-TT.mp4
         (legt zusätzlich reel_JJJJ-MM-TT_titel.png daneben)

Nutzt dieselbe post.json wie insta_post.py, plus den Block "reel":
{
  "band": "MURPHY'S LAW",
  "support": "+ Clobber",                             (optional)
  "hook": "NYHC-Urgestein seit 1982 – Partystimmung garantiert.",
  "hoertipp": "Back with a Bong!",                    (optional)
  "reel": {
    "datum": "2026-11-19",          Pflicht, JJJJ-MM-TT (ein Termin, der wichtigste)
    "club": "Gulfhaus",             Pflicht
    "ort": "Vechta",                Pflicht; Stadt aus der eingebauten Liste
    "lat": 52.73, "lon": 8.29,      nur nötig, wenn der Ort nicht erkannt wird
    "hinweis": "Eintritt frei"      optional
  }
}
Vorlage ist werkzeuge/radar_reel.html (identisch mit dem Radar-Reel-Tool auf claude.ai).
Benötigt: python3-playwright mit Chromium, ffmpeg, npm (für die Schriften über @fontsource).
"""
import base64, json, os, shutil, subprocess, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
FPS, DAUER, TITEL_T = 30, 10.5, 6.6
SCHRIFTEN = [  # (Familie, Stil, Gewicht, Paket, Datei)
    ("Oswald", "normal", 400, "oswald", "oswald-latin-400-normal.woff2"),
    ("Oswald", "normal", 500, "oswald", "oswald-latin-500-normal.woff2"),
    ("Oswald", "normal", 700, "oswald", "oswald-latin-700-normal.woff2"),
    ("Barlow", "normal", 400, "barlow", "barlow-latin-400-normal.woff2"),
    ("Barlow", "italic", 400, "barlow", "barlow-latin-400-italic.woff2"),
]


def schriften_css():
    tmp = tempfile.mkdtemp()
    subprocess.run(["npm", "i", "--silent", "--prefix", tmp, "@fontsource/oswald", "@fontsource/barlow"], check=True)
    css = []
    for fam, stil, gew, pkg, datei in SCHRIFTEN:
        pfad = os.path.join(tmp, "node_modules", "@fontsource", pkg, "files", datei)
        b64 = base64.b64encode(open(pfad, "rb").read()).decode()
        css.append(f"@font-face{{font-family:'{fam}';font-style:{stil};font-weight:{gew};"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    shutil.rmtree(tmp, ignore_errors=True)
    return "<style>" + "".join(css) + "</style>"


def daten(d):
    r = d.get("reel") or {}
    for k in ("datum", "club", "ort"):
        if not r.get(k):
            sys.exit(f"post.json: reel.{k} fehlt")
    return {
        "band": d["band"], "support": d.get("support", ""), "date": r["datum"], "club": r["club"],
        "city": r["ort"], "lat": r.get("lat", ""), "lon": r.get("lon", ""),
        "line": d.get("hook", ""), "hoer": d.get("hoertipp", ""), "note": r.get("hinweis", ""), "cities": True,
    }


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    ziel = os.path.abspath(sys.argv[2])
    titel = os.path.splitext(ziel)[0] + "_titel.png"
    html = open(os.path.join(HIER, "radar_reel.html"), encoding="utf-8").read()
    html = html.replace("</head>", schriften_css() + "</head>", 1)
    arbeit = tempfile.mkdtemp()
    seite = os.path.join(arbeit, "reel.html")
    open(seite, "w", encoding="utf-8").write(html)
    bilder = os.path.join(arbeit, "f")
    os.makedirs(bilder)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1200, "height": 900})
        fehler = []
        pg.on("pageerror", lambda e: fehler.append(str(e)))
        pg.goto("file://" + seite)
        pg.wait_for_function("window.__radar && document.fonts.status==='loaded'", timeout=20000)
        pg.evaluate("Promise.all(['700 100px Oswald','500 40px Oswald','400 40px Oswald','400 40px Barlow','italic 400 40px Barlow'].map(f=>document.fonts.load(f)))")
        geo = pg.evaluate("o=>window.__radar.set(o)", daten(d))
        if not geo:
            sys.exit("Ort nicht erkannt: reel.lat und reel.lon in post.json eintragen.")
        n = int(round(DAUER * FPS))
        for i in range(n + 1):
            url = pg.evaluate(f"(window.__radar.draw({i / FPS:.4f}), document.getElementById('cv').toDataURL('image/png'))")
            open(os.path.join(bilder, f"{i:04d}.png"), "wb").write(base64.b64decode(url.split(",", 1)[1]))
        url = pg.evaluate(f"(window.__radar.draw({TITEL_T}), document.getElementById('cv').toDataURL('image/png'))")
        open(titel, "wb").write(base64.b64decode(url.split(",", 1)[1]))
        b.close()
        if fehler:
            sys.exit("Fehler in der Vorlage: " + "; ".join(fehler))

    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(bilder, "%04d.png"),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", ziel], check=True)
    shutil.rmtree(arbeit, ignore_errors=True)
    print(f"Reel: {ziel}  ({geo['dist']} km {geo['dir']} von Hannover)\nTitelbild: {titel}")


if __name__ == "__main__":
    main()
