# Zurich data preparation

Prepared 21 October 2026 from the complete MEI retrieval of 21 October and the matching rows of Oliver Duntze's GWGesamtliste-Oktober26.xlsx.

## Reproduce

Run python3 scripts/prepare_zurich.py from the repository root. No network access is required. Inputs are data/retrieved/zurich-full.json, data/sources/gw-zurich-editions.json and data/authority/place-authorities.csv.

The GW subset preserves all 16 source columns. It was selected by exact ISTC identifier tokens from the workbook's ISTC column, using the identifiers in the MEI export. There are 1,430 GW rows for 1,419 ISTC identifiers. The full workbook remains the source for future expansions.

## Outputs

- mei-copies.csv, mei-provenance.csv, mei-places.csv and mei-record-links.csv: source-linked views reused from the earlier transformation code. Public copy_id is the MEI record ID; the original copyId remains in the complete snapshot.
- mei-adapter.json: complete records with direct relationship metadata for the reused transformer. Bound-with source data remain in each original record; no provenance is transferred.
- editions.json: all GW candidates and MEI bibliographic statements, kept separate.
- gw-multiple-matches.csv: candidates for nine ISTC identifiers with more than one GW row.
- stations-source.csv: first printing statement, intermediate provenance-place occurrences and last current holding statement for each copy.
- stations-prepared.csv: the same rows with exact, context-free and unambiguous previously reviewed place mappings applied where coordinates were missing. resolution_mapping_id links each reuse to the authority table.
- locations-to-review.csv: grouped unresolved technical cases. This is not yet a specialist-only list.
- subjects.csv: subject and keyword values with HTML entities decoded before delimiter handling. Source spelling is preserved; no synonym merging is applied.
- preparation-summary.json: reproducible counts.

## Interpretation and remaining checks

The 8,778 station rows are evidence entries, not distinct places or proven journeys. Adjacent library/provenance entries have not yet been consolidated for display. Coordinates supplied by MEI have not all been independently verified. Previous mappings are not proof against source errors.

Where there is one GW candidate, the printing place and date both come from that GW row. Year bounds are provisionally extracted from Datum normiert; original Datum remains in editions.json. Uncertainty and alternative printing statements must be reviewed before the public map is built.

For the nine multiple-match editions, printing-place and date fields are deliberately left empty in the station table pending review. Every candidate is retained. No first-candidate fallback or mixing with MEI dates is applied.

No final map dataset or frontend has been deployed. Next: inspect multiple GW matches, resolve straightforward locality cases, then present only genuinely ambiguous places for specialist review.
