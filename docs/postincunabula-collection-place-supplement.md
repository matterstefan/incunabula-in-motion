# Collection and recurring-note locality supplement

24 October 2026. Supplement to station-candidates.json, not a replacement.

## Results

Three narrow rules yield 281 candidate associations concerning 281 catalogue references. 89 references were not covered by the first station list, bringing the distinct union to 409. These are place associations, not dated movements or verified physical-item counts.

- 97 references with the Gal Tz shelfmark prefix: the Handbuch, vol. 3, ZB article, p. 375, identifies this as books from Johann Jakob Simmler's private library. Zurich is inferred from this collection context and his HLS biography. No acquisition date is supplied.
- 174 references linked to notes beginning “Aus dem Vorbesitz des Klosters Rheinau”: institution locality from the existing Handbuch basis. The exact text and prior copy-assignment status are retained.
- 10 references with an explicit Exlibris, Supralibros or Vorbesitz phrase naming the Naturforschende Gesellschaft in Zürich. Locality is supplied by the institutional name; no dates inferred.

All additions are undated. Some duplicate ownership evidence already exists in the first list; use the distinct reference union, not the sum of candidate counts. The 45 baseline reproduction-review references remain included.

## Scope

The two text patterns require previously assigned targets and skip specified uncertainty/negative wording. They do not cover every possible formulation. They do not resolve names mentioned in citations or transfer a note to other copies. No general rules for Zwingli, Gessner, Meyer von Knonau, Simler-labelled owner fields or Ms S shelfmarks were applied. The Gal Tz rule uses collection membership rather than an assumed personal acquisition event.

The recurring-note output includes unresolved fields and repeats across fields; its occurrence counts are not copy counts. It is intended for the next semantic review.

## Reproduce

Run `python3 scripts/expand_postincunabula_collection_places.py` after the station-candidate script. Outputs in the existing export research directory: collection-place-supplement.json, collection-place-summary.json and recurring-provenance-notes.json.

Validation: unique candidate keys, all dates null, and correct union arithmetic (320 + 89 = 409). No map update.
