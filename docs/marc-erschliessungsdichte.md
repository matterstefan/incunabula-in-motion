# Erschliessungsdichte und Provenienz: vereinbarte Auswertungsregeln

Stand: 29. Oktober 2026. Fachliche Präzisierungen aus der gemeinsamen Durchsicht am 27.–28. Oktober; dokumentiert zur Fortsetzung der Arbeit unabhängig vom Chatverlauf.

**Ziel ist die Quantifizierung der im Katalog dokumentierten exemplarspezifischen Informationen je Katalogaufnahme.** Die Zahl kartierbarer Stationen oder normierter Vorbesitzernamen allein beschreibt diese Erschliessungsdichte nicht.

## 1. Zähleinheit und Grundgesamtheit

- Die einzelne Katalogaufnahme zählt einmal, identifiziert durch MARC 001. Mehrere Bände, Teile, Signaturen oder wiederholte Felder erhöhen diese Zahl nicht.
- Bandzahlen und eine Rekonstruktion der Anzahl physischer Exemplare sind für diese Auswertung nicht erforderlich.
- Bei Vorbesitzergruppen zählt jede Kombination aus Vorbesitzer-ID und MARC-ID einmal. Gruppen können sich überschneiden; ihre Summen sind keine Zahl verschiedener Aufnahmen.
- Namen ohne Normdaten-ID bleiben nutzbare Katalogangaben. Sie werden separat als Namensgruppen ausgewiesen und nicht ohne Prüfung mit einer normierten Identität gleichgesetzt.
- Für jede Quote sind Exportdatum, Auswahl, Ausschlüsse, enthaltene Prüffälle und der Nenner in **Aufnahmen** anzugeben. Frühere Nachweisquoten mit der Einheit Record + Institution + Signatur dürfen nicht übernommen werden.
- Keine katalogisierte Angabe bedeutet nicht, dass am Artefakt keine entsprechende Spur vorhanden ist.

Ausgangspunkt ist der vorhandene Export vom 23. Oktober 2026 und seine dokumentierte Arbeitsbasis. Die [Export-Baseline](postincunabula-export-baseline.md) und die [Reproduktionsprüfung](postincunabula-reproduction-screen.md) unterscheiden bereits Aufnahmen und Signaturnachweise. Die dortigen 45 enthaltenen Materialprüffälle sind **Nachweise**, nicht automatisch 45 verschiedene Aufnahmen. Bei einer Aufnahme mit mehreren Nachweisen darf der Ausschluss eines einzelnen Reproduktionsnachweises nicht ungeprüft zum Ausschluss der gesamten Aufnahme führen. Aufnahmen ohne qualifizierenden ZB-Signaturnachweis bleiben gesondert dokumentiert.

## 2. Katalogisate im Zusammenhang lesen

Wo ein Vorbesitzer katalogisiert ist, ist die Aufnahme für die Vorbesitzerauswertung nutzbar. Eine vorherige vollständige Aufteilung auf physische Exemplare ist keine Voraussetzung für die Aufnahmezählung.

Die Felder ergänzen sich:

- 590, 561, 361 und weitere Notizfelder beschreiben Besitzspuren, Einbände, Makulatur, Erwerbungen und andere Exemplareigenschaften.
- 700/710/711 mit entsprechender Rolle erschliessen Personen oder Körperschaften, häufig mit Normdaten-ID.
- 300, 852 und 949 erschliessen Umfang, Signaturen, Teile und lokalen Band-/Exemplarkontext.
- Andere vorhandene Felder werden bei relevantem Inhalt berücksichtigt. Die genannten Tags sind kein abschliessender Evidenzkatalog. Bestellhinweise oder routinemässige Verwaltungsangaben zählen nicht als historische Exemplarinformation.

**590 und 700 können dieselbe Evidenz beschreiben beziehungsweise strukturiert erschliessen.** Ein Vorbesitzereintrag, der aus einem Schenkungsvermerk erschlossen wurde, ist kein unabhängiger zweiter Besitzbeleg. Auch eine Angabe wie „aus der Sammlung“ kann auf Signatur und Sammlungskontext beruhen, ohne dass zusätzlich eine individuelle Besitzspur beschrieben ist.

Originalwortlaut, Feldvorkommen, Unterfelder und vorhandene Einschränkungen bleiben nachvollziehbar. Eine GND-ID macht einen im Text als unsicher bezeichneten Besitz nicht sicher. Namen nur im Freitext dürfen nicht allein deshalb unberücksichtigt bleiben, weil ihnen kein 700er-Feld entspricht.

## 3. Bezug auf Exemplar oder Bandgruppe

Vereinbarte Arbeitshypothese:

1. Bei einem beschriebenen Exemplar gelten Besitzangaben für das ganze Exemplar.
2. Bei einer zusammengehörigen Bandgruppe eines mehrbändigen Werkes gelten sie für die beschriebenen Bände, auch wenn ein Eintrag nur in einem Band steht.
3. Der konkrete Ort einer Spur – etwa „vorderer Spiegel von Teil 7“ – bleibt zusätzlich erhalten. Er begrenzt nach dieser Hypothese nicht automatisch den Umfang des Besitzes.
4. Ausdrückliche Einschränkungen oder abweichende Teilgeschichten im Katalog haben Vorrang.
5. Bei tatsächlich mehreren Exemplaren braucht eine **exemplarbezogene** Aussage eine eindeutige Verbindung zwischen Besitzangabe und Signatur. Wirklich unklare Fälle bleiben auf dieser Ebene offen; die katalogisierte Vorbesitzerangabe bleibt dennoch auf Aufnahmeebene auswertbar.

Mehrere Signaturen bedeuten nicht automatisch mehrere Exemplare. Signaturaufbau, 300 und die Teil-/Bandangaben in 949 sind gemeinsam zu lesen. Eine im Katalog klar erkennbare Bandgruppe soll nicht allein wegen mehrerer Signaturen zum Problemfall werden.

Die bisherigen technischen Kategorien `explicit`, `plausible` und `open` dokumentieren das Verhalten früherer Zuordnungsregeln. Sie sind **keine Bewertung der Erschliessungsdichte oder Verlässlichkeit des Katalogisats**. Insbesondere sind die früher „offenen“ Fälle nicht sämtlich als tatsächlich unklare Katalogangaben nachgewiesen.

## 4. Inhaltliche Dimensionen der Erschliessung

Zunächst getrennte Merkmale pro Aufnahme erfassen, statt voreilig einen einzigen Punktwert zu bilden:

| Dimension | Beispiele |
| --- | --- |
| Vorbesitz und Sammlungszugehörigkeit | Besitzvermerk, Exlibris, Sammlungsangabe, normierter Vorbesitzer |
| Erwerbung und Weitergabe | Schenkung, Widmung, Kauf, ausdrücklich genannte Besitzerfolge |
| Einband | Material, Datierung, Stempel, Werkstatt, Bindungsort |
| Makulatur | verwendete Fragmente, Identifikation des Drucks oder der Handschrift |
| Benutzung und weitere Exemplareigenschaften | Annotationen, Rubrizierung, Kolorierung, Verluste, Ergänzungen |
| Strukturierte Erschliessung | Normdaten-ID, Rollenangabe, expliziter Bezug auf Signatur oder Teil |
| Zeit und Ort | datierte Spur, genannter Ort, Werkstattzuweisung, jeweils mit Unsicherheit und Grundlage |

Druckort und Erscheinungsdatum bleiben wichtige bibliographische Ausgangsinformationen für eine Druckgeschichte. Ihr blosses Vorhandensein ist aber noch kein Mass exemplarspezifischer Erschliessung.

Inhaltliche Information und strukturierte Erschliessung getrennt messen: Ein Besitzvermerk mit 590-Beschreibung und 700/GND-Erschliessung ist eine Besitzinformation mit zusätzlicher strukturierter Erschliessung. Für einfache Abdeckungsquoten zählt das Merkmal je Aufnahme höchstens einmal. Eine spätere Zählung einzelner Spuren oder Ereignisse benötigt eigene, ausdrücklich definierte Regeln.

„Keine“, „knappe“ und „ausführlichere“ exemplarspezifische Erschliessung sind vorerst **zu kalibrierende Kategorien**. Keine festen Schwellen, Gewichtungen oder fertigen Gesamtquoten sind vereinbart. Feldzahl und Textlänge können helfen, Beispiele auszuwählen, ersetzen aber keine inhaltliche Prüfung.

Das Fehlen von Vorbesitzerinformationen darf nicht bereits die Definition geringer Erschliessungsdichte sein. Erst die Kreuzung beider Merkmale soll zeigen, wie stark sie zusammenhängen. Eine ausführliche Einbandbeschreibung kann ohne Vorbesitzerangaben auskommen.

## 5. Historische Stationen, Datierung und Ableitungen

Herstellung, Bindung, Besitz, Schenkung und Sammlungszugehörigkeit können zur Geschichte eines Drucks beitragen. Jede Aussage wird mit ihrer konkreten Grundlage verbunden.

- Ein katalogisierter Bindungsort ist eine mögliche historische Station, auch ohne Vorbesitzernamen.
- Lebensdaten können den möglichen persönlichen Besitz zeitlich eingrenzen. Dieser **biographisch abgeleitete Rahmen** ist kein katalogisiertes Besitzdatum und belegt keinen durchgehenden Besitz während des ganzen Lebens.
- Sammlungsnamen können auch nach dem Tod einer Person weiterverwendet werden.
- Biographische Orte sind nicht automatisch Aufenthaltsorte des Drucks.
- Reihenfolge und unmittelbare Übergaben werden nur soweit angegeben, wie Text oder zeitliche Evidenz sie tragen. Gemeinsame Nennung allein genügt nicht.
- Katalogangabe, Arbeitshypothese und externe Ergänzung bleiben unterscheidbar. Handbuchwissen kann beispielsweise eine Signaturengruppe erklären, ohne einen individuellen Erwerbungsweg zu belegen.

## 6. Gemeinsam besprochene Beispiele

### Augustinus, Opera omnia – Gal Tz 37 | G

MARC-ID: [991000023679705501](https://swisscollections.ch/Record/991000023679705501).

300 nennt elf Teile; 949 erläutert die Verteilung auf die Bände, darunter Teile 1–3 zusammen. 590 beschreibt Besitzeinträge Johann Felix Renners auf Titelblättern, einen Eintrag Kaspar Ulrichs im vorderen Spiegel von Teil 7 und die Zugehörigkeit zur Sammlung J. J. Simler. Die Vorbesitzer sind zusätzlich in 700 mit GND-IDs erschlossen.

Nach der vereinbarten Arbeitshypothese gelten die Besitzangaben für die beschriebene Bandgruppe. Die unterschiedlichen Eintragsorte bleiben erhalten. Es handelt sich um ein informationsreiches Katalogisat, nicht um einen Zuordnungsproblemfall allein wegen der Mehrbändigkeit.

### Christenlich Bilgerschafft – Gal Tz 82 | G

MARC-ID: [991007168889705501](https://swisscollections.ch/Record/991007168889705501).

| Aussage | Grundlage und Grenze |
| --- | --- |
| Druck in [Basel], [Adam Petri], [1512] | Bibliographische Publikationsangabe; Klammern als Quellenunsicherheit erhalten |
| Bindung vermutlich in Ulm | Einbandstempel im Katalog einer Werkstatt des Augustiner-Chorherrenstifts in Ulm zugeordnet; ergänzend Makulatur eines Ulmer Drucks von 1499 im Spiegel |
| Pfyffer und Jesuitenkolleg Luzern | Handschriftliche Widmung von Jodocus Pfyffer an das Kolleg auf dem Titelblatt; der normierte Pfyffer-Vorbesitz ist vermutlich aus diesem Vermerk erschlossen |
| Zugehörigkeit zur Bibliotheca Simleriana | Katalogangabe „aus der Sammlung“; möglicherweise über Signatur und Sammlungskontext bestimmt |
| Heutiger ZB-Bestand | Aktueller Bestandsnachweis |

Die Werkstattzuweisung ist der stärkere Beleg für Ulm: Druckmakulatur allein kann andernorts verwendet worden sein. „Einband der Zeit“ liefert kein genaues Bindungsjahr. Der Weg vom Jesuitenkolleg in Simlers Sammlung und die zeitliche Stellung der Bindung zu den Besitzwechseln sind durch die hier behandelten Angaben nicht vollständig erklärt.

Der in der gemeinsamen Durchsicht von der Projektleitung zitierte Handbuch-Eintrag von Urs Leu zur Bibliotheca Simleriana beschreibt Bücher aus Johann Jakob Simmlers Privatbibliothek. Er erklärt den Sammlungskontext, belegt aber keinen konkreten Transfer dieses Drucks. Die genaue Fundstelle ist bei einer systematischen externen Anreicherung zu ergänzen.

## 7. Bisherige Offline-Ergebnisse und ihre Grenzen

Die separaten Arbeitsdateien vom 27.–28. Oktober 2026 wurden ausserhalb des Repositorys erstellt; dieser Dokumentationsstand importiert sie nicht als neue Projektdaten:

- Revidierte Vorbesitzerbilanz: Katalogisate je Vorbesitzer-ID, unabhängig von den alten technischen Zuordnungskategorien.
- Simler-Auswertung: 308 Aufnahmen; in 39 davon weitere Vorbesitzer in 700/710 mit Vorbesitzerrolle. Die Texte können zusätzliche, nicht strukturiert erschlossene Namen enthalten.
- Die Belege zeigen unter anderem Werkstattzuweisungen, ausdrücklich formulierte Besitzerfolgen, unsichere Besitzangaben und eine Abweichung zwischen einer Besitzdatierung und den Lebensdaten einer erschlossenen Person.

Dies sind Ergebnisse des vorhandenen Teilbestands, keine Gesamtquoten der ZB-Erschliessung. Die historische Übersicht [marc-provenance-coverage-overview.md](marc-provenance-coverage-overview.md) zählt überwiegend Signaturnachweise und verarbeitet auch Anreicherungsschichten. Sie bleibt eine Dokumentation des früheren Verfahrens, nicht die Umsetzung des hier vereinbarten Aufnahmeprofils.

## 8. Nächster Offline-Arbeitsschritt

**Eine kleine, bewusst kontrastierende Auswahl von Aufnahmen aus dem vorhandenen Export gemeinsam prüfen:** Aufnahmen ohne erkennbare historische Exemplarangaben, knappe Beschreibungen und ausführliche Beschreibungen. Die beiden oben besprochenen Fälle dienen als ausführliche Beispiele; ergänzend auch Aufnahmen ohne Vorbesitzereintrag auswählen.

Je Aufnahme eine Zeile mit MARC-ID, Titel/Signatur zur Wiedererkennung, den in Abschnitt 4 genannten Merkmalen, den zugehörigen Originalstellen und einer kurzen Begründung der vorläufigen Dichteklasse anlegen. Dabei alle relevanten Felder gemeinsam lesen, doppelte Erschliessung derselben Evidenz nicht als zusätzliche Spur zählen und routinemässige Verwaltungsangaben ausnehmen.

Aus dieser Durchsicht ein einfaches, nachvollziehbares Raster ableiten. Erst danach die Erkennung auf den vorhandenen Teilbestand anwenden und Treffer sowie Nichttreffer stichprobenweise kontrollieren. Eine gezielt ausgewählte Kalibrierungsstichprobe ist nicht repräsentativ und liefert selbst keine Bestandsquote.

Der grössere Swisscollections-Abruf bleibt bis zur technischen Rückmeldung pausiert; laut Rückmeldung der Projektleitung wurden die Beobachtungen an die IT weitergegeben. Eine vollständige Tranche 1526–1550 ist weiterhin nicht belegt. Nach einer technischen Lösung zuerst die Abrufvollständigkeit prüfen, dann dieselben Auswertungsregeln auf die grössere Grundgesamtheit anwenden.

## 9. Stand der Umsetzung

Diese Ergänzung dokumentiert fachliche Entscheidungen und den nächsten Arbeitsauftrag. Die bisherigen Skripte, Daten und Karten wurden dadurch **nicht** umgestellt. Es wurde kein neuer Katalogabruf oder Analyse-Workflow ausgelöst. Die am 25. Oktober dokumentierten acht Offline-Tests bleiben ein historischer Teststand; sie bestätigen weder das neue Raster noch die Vollständigkeit eines Abrufs.
