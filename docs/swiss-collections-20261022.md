# Swiss MEI collections — 22 October 2026

The complete supplied response to `data.holdingInstitution.country:CH` contains **3,394 distinct MEI records from 21 current holding institutions**. There are 2,475 non-empty ISTC identifiers. This describes MEI coverage on the retrieval date, not the total Swiss incunabula holdings, nor the full holdings of each institution.

The 1,609 Zurich records are identical to the preceding Zurich snapshot. Their documented display decisions remain in use. Original subject and keyword spellings remain visible.

## Reproduce locally

No new CERL requests are made by these commands:

```sh
python3 scripts/prepare_swiss.py
python3 scripts/build_swiss_map.py
node tests/swiss-map.cjs
```

Inputs:

- `data/retrieved/swiss-inventory/swiss-mei-snapshot.json`: original complete MEI response, retrieved 22 October 2026.
- `data/retrieved/swiss-inventory/swiss-institutions.csv`: institutional counts.
- `data/sources/gw-swiss-editions.json`: relevant rows from Oliver Duntze's October 2026 GW export, matched by exact ISTC identifiers.
- `data/authority/zurich-locality-decisions.json` and `swiss-locality-decisions.json`: separate geographical display decisions; GeoNames settlement points (CC BY 4.0).

The first command writes intermediate tables under `data/derived/swiss/`; the second writes the website data under `data/map/`. The existing Zurich preparation files are retained for traceability. Running `build_zurich_map.py` directly restores the Zurich-only map dataset; use `build_swiss_map.py` for the expanded website.

## Coverage and review decisions

- Each MEI record is one displayed copy, identified by its MEI ID. Provenance from other bound-with records is not silently transferred.
- Two Lugano records (`00201370`, `00201413`) lack embedded edition information and an ISTC identifier. They remain visible with their holding and provenance information; no printing statement is invented.
- Three ISTC identifiers have no matching row in the supplied GW subset. Their printing statement comes wholly from the embedded MEI imprint; no GW/MEI place-and-date mixture is created.
- Multiple GW matches are retained. Place/date consensus is used only where the relevant source values agree. Disagreements remain documented in `editions.json`.
- Current libraries are mapped at locality level. Fondation Martin Bodmer uses Cologny and the Eisenbibliothek uses Schlatt TG, following their official addresses. Bourg-Saint-Pierre is a locality approximation from the holding label, not the precise position of the hospice at the pass.
- Breno in MEI `02011741` is identified as Breno (Brescia) by the owner entry and its association with Edolo. Moûtiers is identified by the Tarentaise breviary; Schussenried maps to Bad Schussenried. The incomplete GW spelling `S[peyer` is a display alias for Speyer, supported by the embedded imprint. Source strings are retained.
- All Freiburg printing statements using this mapping specify Freiburg im Breisgau in the embedded MEI imprint.
- Graflingen and the Zurich parish of Seefeld remain unresolved. Country/region labels are retained in details but are not used as local route vertices. Uncertain and alternative printing localities are not silently resolved.
- The four previously identified Zurich coordinate conflicts remain withheld from the map, with the original coordinates retained in the data.
- `data/derived/swiss/unmapped-stations.csv` lists withheld/unlocated stations; `map-review-issues.csv` lists coordinate conflicts and date warnings. This is not a comprehensive scholarly validation of every source coordinate or chronology.

## Interface

The new current-library filter supports multiple choices (OR). Libraries, MEI terms, printing places, languages and text search combine with AND. Library counts reflect the other filters; clearing the library selection includes all 21 institutions. The existing saved selection remains independent of subsequent searches and filters.

There are 17,565 station rows; this is not a count of distinct places or proven journeys. Consecutive co-located stations may be combined for display. The timeline carries the last recorded location forward without asserting continuous residence.

## Verification

Automated checks exercise every copy detail, historical timeline exclusions, all current holding locations, Zurich coordinate exclusions, the unresolved Seefeld station, library OR/other-filter AND, missing edition references and saved multi-search selections. Browser checks confirmed Solothurn (1,070), Zurich plus Solothurn (2,679), clearing/resetting the filter, circles and the heatmap for all 3,394 records at 17 current locality points.
