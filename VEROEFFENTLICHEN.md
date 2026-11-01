# Morgens veröffentlichen

Die geplanten Aufgaben (Frühausgabe 2:54 Uhr, Konzert-Radar 3:30 Uhr) können nicht pushen.
Sie legen ihre Ausgabe auf Claude-Seiten ab. Ein Chat bringt sie von dort auf die Website.

## Ablauf
1. Repo mit Schreibzugriff anhängen (add_repo, access "push") und klonen.
2. **Frühausgabe:** Artifact read `https://claude.ai/artifact/E37KgyL3yN99UZBJCGBoR2`
   - mit `path: "ausgabe.json"` holen und als `ausgaben/JJJJ-MM-TT.json` speichern (Datum aus dem Kopf der Seite).
   - Fehlt ausgabe.json: mit `path: "index.html"` holen und
     `python3 -I werkzeuge/aus_html.py <index.html> ausgaben/JJJJ-MM-TT.json` ausführen.
   - Steht im Kopf nicht das heutige Datum: Frühausgabe weglassen und das melden.
3. **Konzert-Radar:** Artifact read `https://claude.ai/artifact/XoSEuKd8oMYU9t12FGt2j2` mit `path: "index.html"`,
   als `konzerte/index.html` speichern – nur wenn die Datumszeile heute zeigt.
   Achtung: Die Claude-Seite liefert das Dokument in einer Hülle; nur das innere Dokument (zweites `<!doctype html>` bis zum zugehörigen `</html>`) übernehmen. Gleiches gilt für index.html der Frühausgabe.
4. `python3 render.py` – baut Frühausgabe, Archiv, Sitemap **und** das Radar-Archiv (konzerte/JJJJ-MM-TT/, konzerte/archiv/).
   Danach index.html mit der Claude-Seite der Frühausgabe vergleichen (Inhalt muss gleich sein).
5. Commit (user.name "Hilmer Jahnke", user.email "brainesworld@gmail.com", Nachricht „Frühausgabe JJJJ-MM-TT“),
   `git fetch origin main`, rebase, nach main pushen.
6. Nach ~60 s https://fruehausgabe.hilmerjahnke.de/?v=<Uhrzeit> und /konzerte/ prüfen.
