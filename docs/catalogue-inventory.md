# Automatisches Aufnahmeinventar

Stand 3. November 2026. Die Projektleitung akzeptiert die 12’315 Aufnahmen des SRU-Laufs 41628680684 (1551–1600) als ausreichend vollständigen Arbeitsbestand. Die technische Differenz von einer Aufnahme bleibt separat dokumentiert. Es erfolgt kein erneuter Katalogabruf.

## Wiederholen

Actions → **Inventory Zurich catalogue records offline** → Run workflow. Die Vorgaben verwenden das gespeicherte Artefakt des genannten SRU-Laufs. Für weitere Tranchen die Run-ID und den exakten Artefaktnamen ändern. GitHub-Artefakte laufen nach 30 Tagen ab; ein bereits heruntergeladenes ZIP kann unabhängig davon lokal verarbeitet werden:

```sh
python scripts/inventory_catalogue_records.py QUELLE.zip --output inventar
```

Das Skript benötigt nur die Python-Standardbibliothek. Es liest ausschliesslich XML aus `pages/`, ignoriert Diagnosekopien und macOS-Metadaten, dedupliziert nach MARC 001 und bricht bei widersprüchlichen Versionen ab. Es speichert Quellprüfsumme, Query, technischen Abrufstatus und Nenner.

## Regeln

Eine Aufnahme pro MARC 001; jedes Merkmal höchstens einmal je Aufnahme. Kein Zählen physischer Exemplare, Bände oder Provenienzereignisse. Mehrere Signaturen machen eine Aufnahme nicht zum Problemfall. Alle gelieferten Aufnahmen bleiben enthalten, auch Reproduktionen; keine zusätzlichen Material- oder Jahresfilter.

Strukturierte Vorbesitzer: 700/710/711 mit Name und Rolle `fmo` oder unterstützter Rollenbezeichnung. Normdatenkennung ($0/$1), GND-Kennung und Namen ohne Kennung werden getrennt erfasst; diese Gruppen können sich überschneiden.

Textinventar: 361, 541, 561, 562, 563, 565, 590, 591, 595, 596. Nur Felder mit nichtleerem alphabetischem Unterfeld zählen als Text, reine Linkage-/Institutionsnummern nicht. Feldpräsenz ist keine Bestätigung historischer Relevanz: administrative Texte bleiben zur Durchsicht enthalten. Private 361/541/561 (Indikator 0) werden ausgelassen; betroffene Aufnahmen separat gezählt.

Suchwortsignale für Besitz, Einband, Makulatur, Benutzung und Schenkung sind ausdrücklich ungeprüfte Kandidaten. Sie durchsuchen die gewählten Notizen und 500. Die vollständigen Muster stehen im Skript. Negationen, Unsicherheiten, gedruckte Widmungen und fremde Exemplarbezüge werden noch nicht semantisch aufgelöst. Keine Schätzung der Zahl historischer Ereignisse und keine Klassifikation in geringe/mittlere/hohe Dichte.

300, 500, 852, 949 und alle ausgegebenen Originalunterfelder bleiben für die gemeinsame Lektüre erhalten. Explizite $5-Zuordnungen werden separat ausgewiesen; Aussagen über bestimmte ZB-Exemplare erfordern die Prüfung dieser Zuordnungen. Feldzählungen betreffen zunächst die gesamte Aufnahme. Namen ausschliesslich im Freitext sind nicht in der Zahl strukturierter Vorbesitzer enthalten.

## Ergebnisse

- `Uebersicht.html`: lesbare Übersicht und zwölf gezielt kontrastierende Beispiele.
- `summary.json`: alle Kennzahlen mit Nenner, Quellenangaben und Abrufstatus.
- `records.jsonl`: genau eine Datenzeile pro Aufnahme mit Merkmalen und Originalbelegen.
- `review-sample.json`: Originalstellen der gezielten Beispiele, keine repräsentative Stichprobe.

Erster Lauf: 3’416 Aufnahmen mit strukturierten Vorbesitzern; 5’163 mit ausgewählten Notizen; 5’221 mit mindestens einem dieser beiden Merkmale; 7’094 ohne beide. Das Fehlen dieser Merkmale ist keine abschliessende Aussage über Informationsarmut. Die Methode ist eine vorbereitende Feld- und Signalbestandsaufnahme gemäss `marc-erschliessungsdichte.md`, kein fertig kalibriertes Dichtemass.
