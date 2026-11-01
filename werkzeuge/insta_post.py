#!/usr/bin/env python3
"""Baut das Instagram-Bild (1080x1350) zum Tipp des Tages im Konzert-Radar-Look.

Aufruf:  python3 werkzeuge/insta_post.py post.json ausgabe.jpg
post.json:
{
  "eyebrow": "TIPP DES TAGES",
  "band": "FIFTH ANGEL",
  "support": "+ Leatherwitch",                      (optional)
  "termine": ["Do 5.11. · Bambi Galore, Hamburg", "Fr 6.11. · MTS, Oldenburg"],
  "hook": "Das Kult-Debüt von 1986 – komplett live", (optional, kurz)
  "hoertipp": "Wings of Destiny"                     (optional)
}
Schriften (Anton, Oswald) werden bei Bedarf über npm/@fontsource nachinstalliert.
"""
import json, math, os, subprocess, sys, tempfile

BG = "#141210"; INK = "#f3eee4"; RED = "#c0261d"; RED2 = "#7d1a14"; MUTED = "#a39a8e"


def schriften():
    have = subprocess.run(["fc-list"], capture_output=True, text=True).stdout
    if "Anton" in have and "Oswald" in have:
        return
    from fontTools.ttLib import TTFont  # pip install --break-system-packages fonttools brotli
    tmp = tempfile.mkdtemp()
    subprocess.run(["npm", "i", "--silent", "--prefix", tmp, "@fontsource/anton", "@fontsource/oswald"], check=True)
    os.makedirs(os.path.expanduser("~/.fonts"), exist_ok=True)
    base = os.path.join(tmp, "node_modules", "@fontsource")
    for src, dst in [("anton/files/anton-latin-400-normal.woff2", "Anton.ttf"),
                     ("oswald/files/oswald-latin-500-normal.woff2", "Oswald-Medium.ttf"),
                     ("oswald/files/oswald-latin-300-normal.woff2", "Oswald-Light.ttf")]:
        f = TTFont(os.path.join(base, src)); f.flavor = None
        f.save(os.path.expanduser("~/.fonts/" + dst))
    subprocess.run(["fc-cache", "-f"], check=True)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def radar(cx, cy, R):
    p = []
    for i in range(1, 6):
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{R*i/5:.0f}" fill="none" stroke="{RED2}" stroke-width="3"/>')
    p.append(f'<line x1="{cx-R}" y1="{cy}" x2="{cx+R}" y2="{cy}" stroke="{RED2}" stroke-width="2"/>')
    p.append(f'<line x1="{cx}" y1="{cy-R}" x2="{cx}" y2="{cy+R}" stroke="{RED2}" stroke-width="2"/>')
    a0, a1 = math.radians(-118), math.radians(-72)
    x0, y0, x1, y1 = cx+R*math.cos(a0), cy+R*math.sin(a0), cx+R*math.cos(a1), cy+R*math.sin(a1)
    p.append(f'<path d="M{cx},{cy} L{x0:.0f},{y0:.0f} A{R},{R} 0 0 1 {x1:.0f},{y1:.0f} Z" fill="url(#sw)"/>')
    p.append(f'<line x1="{cx}" y1="{cy}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>')
    for r, a, s in [(.55, -140, 14), (.85, -95, 12), (.4, -55, 10), (.75, -30, 15)]:
        bx, by = cx+R*r*math.cos(math.radians(a)), cy+R*r*math.sin(math.radians(a))
        p.append(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{s*2.4:.0f}" fill="{RED}" opacity=".25"/><circle cx="{bx:.0f}" cy="{by:.0f}" r="{s}" fill="{RED}"/>')
    return "".join(p)


def bandzeile(band):
    """Schriftgröße so wählen, dass der Bandname in 960 px passt (Anton ~0.47 em je Zeichen)."""
    n = max(len(band), 1)
    return max(90, min(230, int(960 / (0.47 * n))))


def baue(d, out):
    W, H = 1080, 1350
    band = d["band"].upper()
    fs = bandzeile(band)
    y = 330
    teile = [f'<text x="540" y="{y}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="54" fill="{RED}" letter-spacing="16">{esc(d.get("eyebrow","TIPP DES TAGES"))}</text>']
    y += 40 + fs
    teile.append(f'<text x="540" y="{y}" text-anchor="middle" font-family="Anton" font-size="{fs}" fill="{INK}" letter-spacing="4">{esc(band)}</text>')
    if d.get("support"):
        y += 80
        teile.append(f'<text x="540" y="{y}" text-anchor="middle" font-family="Oswald" font-weight="300" font-size="60" fill="{INK}">{esc(d["support"])}</text>')
    y += 70
    teile.append(f'<rect x="390" y="{y}" width="300" height="8" fill="{RED}"/>')
    y += 20
    for t in d.get("termine", [])[:3]:
        y += 78
        teile.append(f'<text x="540" y="{y}" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="54" fill="{INK}">{esc(t)}</text>')
    if d.get("hook"):
        y += 110
        teile.append(f'<text x="540" y="{y}" text-anchor="middle" font-family="Oswald" font-weight="300" font-size="50" fill="{MUTED}">{esc(d["hook"])}</text>')
    if d.get("hoertipp"):
        y += 72
        teile.append(f'<text x="540" y="{y}" text-anchor="middle" font-family="Oswald" font-weight="300" font-size="44" fill="{MUTED}">Hörtipp: „{esc(d["hoertipp"])}“</text>')
    teile.append(f'<text x="540" y="1270" text-anchor="middle" font-family="Anton" font-size="56" fill="{INK}" letter-spacing="10">KONZERT-RADAR</text>')
    teile.append(f'<text x="540" y="1318" text-anchor="middle" font-family="Oswald" font-weight="500" font-size="30" fill="{MUTED}" letter-spacing="5">METAL &amp; ROCK RUND UM HANNOVER · LINK IN BIO</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><radialGradient id="sw" cx="0" cy="0" r="1"><stop offset="0" stop-color="{RED}" stop-opacity=".05"/><stop offset="1" stop-color="{RED}" stop-opacity=".4"/></radialGradient>
<radialGradient id="glow" cx=".5" cy=".45" r=".7"><stop offset="0" stop-color="#2a1a16"/><stop offset="1" stop-color="{BG}"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="url(#glow)"/><g opacity=".55">{radar(540, 1500, 1150)}</g>{"".join(teile)}</svg>'''
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, "p.svg"), "w", encoding="utf-8").write(svg)
    png = os.path.join(tmp, "p.png")
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), os.path.join(tmp, "p.svg"), "-o", png], check=True)
    from PIL import Image
    Image.open(png).convert("RGB").save(out, quality=95)


if __name__ == "__main__":
    schriften()
    baue(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
    print("gebaut:", sys.argv[2])
