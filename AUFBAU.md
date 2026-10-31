# Hannover Frühausgabe – Aufbau einer Ausgabe

Jeden Morgen entsteht **eine Datei** `ausgaben/JJJJ-MM-TT.json`. Danach `python3 render.py` ausführen, alles committen und nach `main` pushen. Vercel veröffentlicht automatisch unter https://fruehausgabe.hilmerjahnke.de.

## JSON-Format

```json
{
  "kurz": ["5–6 Punkte für „Das Wichtigste in 90 Sekunden“, inkl. Sport. <b>Konkretes Detail</b> fett."],
  "ressorts": [
    {
      "id": "hannover | deutschland | welt | sport | netz",
      "hinweis": "optional, z. B. „Reddit war heute nicht erreichbar.“",
      "meldungen": [
        {
          "titel": "Schlagzeile",
          "kurz": "1–2 Sätze, konkretes Detail in <b>…</b>",
          "bewertung": "gesichert | plausibel | vorsicht",
          "lang": ["1–2 kurze Absätze, komplett in eigenen Worten"],
          "einschaetzung": "Ein Satz: warum diese Bewertung",
          "quellen": [{"name": "Quelle", "url": "https://…"}]
        }
      ]
    }
  ],
  "faktencheck": ["2–4 Punkte: wo man genau hinschauen sollte"],
  "woche": ["Termine, Spiele, Wetter Hannover, konkrete Tipps"]
}
```

Reihenfolge der Ressorts: hannover, deutschland, welt, sport, netz. Pro Ressort 3–4 Meldungen.

## Regeln für die öffentliche Web-Version

- **Eigene Worte:** Keine Sätze oder Absätze aus Artikeln übernehmen. Höchstens ein kurzes Zitat (unter 15 Wörtern) pro Quelle, nur wenn der genaue Wortlaut wichtig ist. Langfassung höchstens 2 kurze Absätze, den Aufbau des Originalartikels nicht nachbauen.
- **Jede Meldung braucht mindestens eine verlinkte Quelle.** Nichts erfinden, lieber weniger Meldungen.
- Nur Meldungen der letzten ~48 Stunden (montags: das Wochenende).
- Überraschende Behauptungen mit einer zweiten Quelle gegenprüfen; Widersprüche offen benennen.
- Gesperrte Seiten nicht über Umwege abrufen; im Ressort-`hinweis` vermerken.
- Keine Fotos, keine Namen von Privatpersonen (Blaulicht-Meldungen ohne Namen), keine persönlichen Anspielungen auf den Herausgeber.
- Nur `<b>` als Formatierung, kein anderes HTML.
- Bereits vorhandene Ausgaben-Dateien nie ändern oder löschen.
