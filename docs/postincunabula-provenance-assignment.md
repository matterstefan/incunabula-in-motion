# Provenance assignment across the all-ZB working corpus

23 October 2026. Offline, conservative field-level association. No map changes.

## Units and results

The baseline remains 5,149 catalogue references in 4,396 records, including 45 reproduction-review references. We analyse 2,524 provenance fields or lexical note candidates: 96 explicitly linked, 2,238 plausibly linked and 190 unresolved fields. Repeated descriptions of the same owner/event are not deduplicated into events.

Mutually exclusive reference coverage, prioritising explicit over plausible:

| Category | References |
|---|---:|
| At least one explicitly linked field/candidate | 59 |
| Plausible links, no explicit link | 1,122 |
| Only unresolved field/candidate context | 170 |
| No assigned candidate and no unresolved candidate in record | 3,798 |
| Total | 5,149 |

A reference with explicit or plausible evidence may also have unresolved fields; consult open_fields_in_record. The final category is not proof that a copy lacks provenance: unrecognised wording and information outside this export remain possible. Candidates attributed only to another reference do not count for this reference.

## Assignment rules

- Same-field 949$b and $j match the retained reference exactly: explicit association of that 949 note only.
- A complete shelfmark appears in the source field's $3/$5 and resolves to one retained reference without a cross-institution shelfmark collision: explicit. Complex or negative scope wording remains open.
- A record has exactly one complete 852 institution/shelfmark pair, one retained reference and no field scope qualifier: plausible, not explicit.
- An unambiguous ZB institution-only scope and a single retained ZB reference can support a plausible link.
- Otherwise leave the field unresolved. The reviewed Biel record remains unresolved for record-level fields regardless of the generic rules.

Explicit means explicit copy linkage within the catalogue. It does not make an uncertain ownership claim certain or verify the identity/number of physical artifacts.

Core provenance fields/owner roles and lexical note candidates remain distinguishable. Generic stamp mentions alone are not selected. Other note candidates still require semantic interpretation. No scope is transferred between neighbouring fields.

## Place and time inspection

356 references have linked fields with place tokens from a deliberately limited vocabulary; 226 have linked note fields with four-digit year tokens. These are not counts of usable map stations. Years may describe citations, bindings or other events. Person lifespan dates in owner fields are not extracted as ownership dates. Place matches can occur in institutional names and are not yet geocoded. Neither token absence nor co-occurrence establishes historical absence/presence or an event relationship.

Orelli/Hagenbuch biographical decisions remain in review-decisions.json as separate case-specific enrichment; they are not silently inserted into source text or applied globally. The next step is event interpretation, chronology and place resolution, using those reviewed decisions.

## Files and rerun

Run after the baseline, reproduction, field-inventory and item-context scripts:

```sh
python3 scripts/assign_postincunabula_provenance.py /path/to/2026-10-23-17h15.zip
```

Outputs in data/research/zurich-postincunabula-export-20261023:

- provenance-assignments.json: original subfields, classification, reasons, targets and text tokens.
- provenance-coverage.json: one entry for every retained reference, including those without linked evidence.
- provenance-assignment-summary.json: counts and caveats.

Validated unchanged reference count, explicit Plinius scope, plausible Hagenbuch note, unresolved Biel fields, Rheinau association only with RRr 125, rejection of the binding-stamp negative control, and absence of owner lifespan dates from year-token extraction.
