# Automated post-incunabula evidence profile

Offline analysis of the saved swisscollections snapshot; 23 October 2026. Counts refer to bibliographic records, not uniquely identified copies. No network retrieval.

Analysed 3930 retained records; found 303 distinct owner keys. Authority-based grouping remains provisional where identifiers or aliases differ.

## Reusable owner groups

| Top owner groups | Distinct records covered (union) |
|---|---:|
| 5 | 596 |
| 10 | 689 |
| 20 | 741 |
| 50 | 805 |

## Candidate extraction

These counts describe literal text matches, not verified events. The small place lexicon is recorded in the JSON output.

| Indicator | Records |
|---|---:|
| provenance_cue_outside_561_361 | 301 |
| provenance_note_candidate | 789 |
| explicit_place_string | 306 |
| date_string | 254 |
| place_and_date_same_note | 89 |
| additional_records_from_other_note_cues | 18 |

## Repeated notes

| Note (abbreviated) | Records |
|---|---:|
| Aus dem Vorbesitz des Klosters Rheinau | 83 |
| Teil einer 1899 von Gerold Meyer von Knonau dem in der Stadtbibliothek eingerichteten "Zwingli-Museum" vermachten Sammlung zum Reformationsjubiläum 1819 | 20 |
| Aus dem Vorbesitz des Klosters Rheinau, auf vorderem Spiegel Exlibris mit Legende: "Sub abate Romano I." | 14 |
| Aus dem Besitz Huldrych Zwinglis. | 12 |
| Aus dem Vorbesitz von Hansjürg Zimmermann, mit Initialen auf dem vorderen Vorsatzblatt. Hanschr. Besitzvermerke von Rudolph Wonlich, Rudolf Zimmermann (1768), Theophil Zimmermann ( | 10 |
| Aus dem Vorbesitz des Klosters Rheinau, Verbalexlibris auf dem Titelblatt | 9 |
| Aus dem Besitz Huldrych Zwinglis. Mit Annotationen von seiner Hand. | 9 |
| Aus dem Vorbesitz Huldrych Zwinglis. | 9 |
| Aus dem Besitz Huldrych Zwinglis. Mit wenigen Annotationen von seiner Hand. | 8 |
| Verbalexlibris von Werner Steiner auf dem vorderen Vorsatzblatt. Teil einer 1899 von Gerold Meyer von Knonau dem in der Stadtbibliothek eingerichteten "Zwingli-Museum" vermachten S | 8 |
| Aus dem Vorbesitz Huldrych Zwinglis. Mit wenigen Annotationen von seiner Hand. | 7 |
| Handschriftliche Einträge und Unterstreichungen mit schwarzer Tinte | 7 |

## Boundaries and next step

Each candidate retains record, source field occurrence, complete text, subfields, shelfmarks and matched text spans. Multiple-shelfmark records are marked for unresolved scope. Public note text only is analysed; personal life dates in name headings are not used. Numeric dates embedded in notes can still refer to literature or biography. No chronology is inferred from field order.

Prioritise the most frequent institutional owner groups and repeated formulations. Check a small sample of each rule before interpreting candidate text as an event. Use the handbook as explicitly sourced enrichment only. Person-to-place assignments and inferred residence periods are not part of this run.

## Spot check

Eight candidate notes with both place and date strings were read. The check confirms why co-occurrence must not become an automatic event: 991012318469705501 mentions a sixteenth-century Zurich priest and Rheinau in the same note, without dating Rheinau ownership. 991067602879705501 explicitly refers to evidence on a preceding bound print. 991041964639705501 marks Jesuit-college ownership as uncertain. Conversely, 991147752079705501 explicitly quotes a Wettingen ownership note dated 1639. This small check validates candidate retention, not automatic event extraction precision.

An optional manual GitHub workflow, Analyse saved post-incunabula evidence, reproduces the analysis offline and uploads results. No need to run it for the supplied outputs.
