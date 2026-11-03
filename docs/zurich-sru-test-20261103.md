# SRU-Kontrolllauf: Alte Drucke Zürich, 1551–1600

Vorbereitet am 3. November 2026 nach der Rückmeldung aus Basel. Dieser manuell gestartete Kontrolllauf hebt die frühere Abrufpause für den hier beschriebenen Test auf.

## Start

Unter **Actions → Test Zurich old prints SRU → Run workflow** den Branch `main` wählen. Vorgaben: **1551** und **1600**. Dann **Run workflow** anklicken. Das Vorbereiten dieses Workflows startet keinen Abruf.

## Auswahl und Aussagegrenzen

Der Lauf verwendet Z01–Z06, `dc.format = PR` sowie `dc.date >= 1551 AND dc.date <= 1600`. Diese Abfrage setzt den Kontrollversuch vom 3. November fort; sie ist ein Belastungs- und Vollständigkeitstest für diese SRU-Auswahl. Die 12’869 vom Nutzer gemeldeten Webtreffer sind keine verbindliche Sollzahl: Die Gleichwertigkeit von Webfacetten und SRU-Indices ist noch ungeklärt. Getrennte Datumsbedingungen können bei mehrwertigen Jahresangaben unerwartete Treffer liefern. Der Lauf ist keine geprüfte Grundgesamtheit originaler Drucke und keine Erschliessungsdichte-Auswertung.

Beim vorangegangenen Test 1526–1550 wurden ohne Timeout und Duplikate 5’360 eindeutige Aufnahmen bei gemeldeten 5’361 geliefert; die letzte Seite blieb leer. Deshalb werden solche Lücken nicht als Erfolg gewertet.

## Ablauf und Ergebnisse

- Jeder Lauf und jede Wiederholung beginnt frisch in einem eigenen Ordner; keine alten Cache-Seiten.
- 100 Records pro Seite; mindestens zwei Sekunden zwischen Anfragestarts; 300 Sekunden Timeout je Anfrage und bis zu vier Versuche bei Transportfehlern.
- Höchstens fünf Stunden Abrufzeit; der Job lässt zusätzliche Zeit zum Sichern der Ergebnisse.
- Exakte Query in `request-v4.json`; rohe XML-Seiten, Antwortdiagnostik, Seiten-URLs, Duplikate und Konflikte bleiben erhalten.
- Gezählt werden eindeutige MARC-001-Aufnahmen. Die ältere Profilierung enthält zusätzlich Referenzzahlen; diese sind keine Bandzählung und keine Umsetzung der neu vereinbarten Dichte-Methode.
- Die Laufübersicht zeigt gemeldete, gelieferte und eindeutige Records sowie Lücken. Unvollständige oder ungeprüfte Abdeckung führt zu einem fehlgeschlagenen Prüfstatus, auch wenn Daten gespeichert wurden.
- Unter **Artifacts** das ZIP herunterladen; Aufbewahrung 30 Tage. Teilresultate werden auch nach Fehlern hochgeladen, soweit der Runner noch weiterarbeiten kann. Bei hartem Zeitlimit kann das Abschlussprotokoll fehlen; vorhandene Seiten und Fortschrittsdateien bleiben als Teilresultat.
- Keine automatischen Commits, Kartenänderungen oder Veröffentlichung der Daten auf der Website.

Der ursprüngliche Workflow `Collect Zurich date tranche` bleibt für ältere Aufrufe unverändert; für diesen Test ausdrücklich **Test Zurich old prints SRU** verwenden.
