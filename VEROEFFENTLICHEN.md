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

## Instagram-Post zum Tipp des Tages (nach dem Veröffentlichen)
1. Aus konzerte/index.html den „Tipp des Tages“ nehmen (Band, Support, Termine, Hörtipp).
2. Instagram-Handles NUR übernehmen, wenn bestätigt: verifiziertes Profil (blauer Haken) in der Instagram-Suche, Band-Link der Radar-Seite, offizielle Band-/Label-/Agentur-Seite oder Link von Hilmer. Nie raten. Ohne bestätigten Handle: nicht markieren, Hilmer nach dem Link fragen.
3. post.json schreiben, inkl. Block `"reel"` mit EINEM Termin (der nächstgelegene/wichtigste): `datum` (JJJJ-MM-TT), `club`, `ort`; optional `hinweis` (z. B. „Eintritt frei“). `hook` = ein Satz, warum man hingehen sollte (eigene Worte, max. ~90 Zeichen).
4. **Radar-Reel (Hauptformat):** `python3 -I werkzeuge/radar_reel.py post.json reel_JJJJ-MM-TT.mp4` (braucht python3-playwright mit Chromium, ffmpeg, npm; Schriften lädt das Skript selbst; Dauer ca. 1,5 Min.). Ergibt ein stummes 10,5-s-Reel (1080×1920: Radar mit Hannover in der Mitte findet den Ort → Tipp-Karte → „Kalender – Link in Bio“) und `reel_JJJJ-MM-TT_titel.png` als Titelbild. Meldet das Skript „Ort nicht erkannt“: Koordinaten des Orts als `reel.lat`/`reel.lon` eintragen und neu starten. Die Vorlage `werkzeuge/radar_reel.html` ist dasselbe Tool wie https://claude.ai/artifact/4N6CRHNc36LK9QXDRwp1Fj – Änderungen an beiden Stellen nachziehen.
5. **Bild (Ersatz):** `python3 werkzeuge/insta_post.py post.json insta_post_JJJJ-MM-TT.jpg` (pip: fonttools brotli; Schriften lädt das Skript selbst). Nur schicken, wenn das Reel nicht gebaut werden konnte.
6. Reel und Titelbild per SendUserFile schicken (sonst das Bild); per SendUserMessage: Bildunterschrift zum Kopieren (eigene Worte, Termine, Hörtipp, Hinweis „Link in Bio“, „Termine ohne Gewähr“, 8–12 Hashtags), den Hinweis „Musik in der App aus der Musikbibliothek drüberlegen, am besten den Hörtipp: <Songtitel>“ plus Uhrzeit-Empfehlung (wochentags ca. 18:30, Sa/So ca. 11:00).
7. Hilmer lädt in der Instagram-App als Reel hoch, legt die Musik drüber, wählt das Titelbild, fügt die Bildunterschrift ein und plant den Beitrag über „Erweiterte Einstellungen → Diesen Beitrag planen“ auf die empfohlene Uhrzeit.
8. send_later auf Uhrzeit + 5 Min legen. Dann im Browser (konzert_radar_hannover): neuesten Beitrag öffnen, Bildunterschrift prüfen, bestätigte Handles markieren (Beitrag → ⋯ → Bearbeiten → „Personen markieren“), DMs an Band(s) und Veranstaltungsort (deutsche Bands/Orte auf Deutsch, sonst Englisch). Reels über /p/<code>/ öffnen, nicht /reel/<code>/. Manche Konten erlauben keine Markierung (z. B. frozencrownofficial) – dann nur DM. EXIL Göttingen nimmt keine DMs an.
