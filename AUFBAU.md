# Hannover Frühausgabe – Aufbau einer Ausgabe

Jeden Morgen entsteht **eine Datei** `ausgaben/JJJJ-MM-TT.json`. Danach `python3 render.py` ausführen, alles committen und nach `main` pushen. Vercel veröffentlicht automatisch unter https://fruehausgabe.hilmerjahnke.de.

## JSON-Format

```json
{
  "stand": "Stand: Samstag, 5 Uhr",
  "kurz": ["5–6 Punkte für „Das Wichtigste in 90 Sekunden“, inkl. Sport. <b>Konkretes Detail</b> fett."],
  "ressorts": [
    {
      "id": "hannover | deutschland | welt | sport | netz",
      "untertitel": "optional, sonst Standard (z. B. „Vor der Haustür“)",
      "hinweis": "optional, z. B. „Reddit war heute nicht erreichbar.“",
      "trends": [{"begriff": "suchbegriff", "volumen": "200+", "anlass": "kurzer Anlass"}],
      "meldungen": [
        {
          "titel": "Schlagzeile",
          "kurz": "1–2 Sätze, konkretes Detail in <b>…</b>",
          "liste": ["optional: Stichpunkte für eine „Kurz notiert“-Karte"],
          "bewertung": "gesichert | plausibel | vorsicht",
          "orte": ["Ernst-August-Platz Hannover", {"name": "ZAG Arena", "suche": "ZAG Arena Hannover"}],
          "lang": ["1–2 kurze Absätze, komplett in eigenen Worten"],
          "einschaetzung": "Ein Satz: warum diese Bewertung",
          "quellen": [{"name": "Quelle", "url": "https://…"}]
        }
      ]
    }
  ],
  "faktencheck": ["2–4 Punkte: wo man genau hinschauen sollte"],
  "woche": [
    {"wann": "Sa 31. Okt", "titel": "Kurzer Titel", "text": "Wetter Hannover, Termine, Spiele, <b>Uhrzeiten</b>"},
    {"wann": "So 1. Nov", "titel": "…", "text": "…"},
    {"wann": "Mo 2. bis Fr 6. Nov", "titel": "…", "text": "…"}
  ]
}
```

Reihenfolge der Ressorts: hannover, deutschland, welt, sport, netz. Pro Ressort 3–4 Meldungen.

### Pflicht-Elemente (so sieht die Zeitung aus)
- **Ressort „netz“ immer mit `trends`:** 5–8 Kacheln aus dem Google-Trends-RSS (Begriff, Suchvolumen, Anlass in wenigen Wörtern). Darunter 2–3 Meldungen zu den spannendsten Trends.
- **`orte` bei jeder Meldung mit klarem Ort** (Demo-Treffpunkt, Stadion, Unfallort, Stadt im Ausland): erzeugt die ◎-Karte-Links zu Google Maps. Konkrete, eindeutige Suchbegriffe verwenden (Ort + Stadt). Keine Privatadressen.
- **Je Ressort gern eine „Kurz notiert“-Karte** (Titel „Kurz notiert“, Punkte in `liste`) für kleinere Meldungen.
- **`woche` als genau 3 Tageskacheln** (heute, morgen, Rest der Woche) mit Wetter Hannover, Spielen und Terminen.
- `stand` mit Wochentag und Uhrzeit der Recherche.
- Korrekturen zu Fehlern der Vortagsausgabe im `faktencheck` als erster Punkt („<b>Korrektur:</b> …“).

## Regeln für die öffentliche Web-Version

- **Eigene Worte:** Keine Sätze oder Absätze aus Artikeln übernehmen. Höchstens ein kurzes Zitat (unter 15 Wörtern) pro Quelle, nur wenn der genaue Wortlaut wichtig ist. Langfassung höchstens 2 kurze Absätze, den Aufbau des Originalartikels nicht nachbauen.
- **Jede Meldung braucht mindestens eine verlinkte Quelle.** Nichts erfinden, lieber weniger Meldungen.
- Nur Meldungen der letzten ~48 Stunden (montags: das Wochenende).
- Überraschende Behauptungen mit einer zweiten Quelle gegenprüfen; Widersprüche offen benennen.
- Gesperrte Seiten nicht über Umwege abrufen; im Ressort-`hinweis` vermerken.
- Keine Fotos, keine Namen von Privatpersonen (Blaulicht-Meldungen ohne Namen), keine persönlichen Anspielungen auf den Herausgeber.
- Nur `<b>` als Formatierung, kein anderes HTML.
- Bereits vorhandene Ausgaben-Dateien nie ändern oder löschen.
