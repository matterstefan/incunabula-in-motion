# ZB postincunabula: revised export baseline

Offline analysis of the user's swisscollections export `2026-10-23-17h15.zip`, 23 October 2026. This supersedes the Z06-only population for the planned all-ZB assessment. The older analyses remain historical, narrower analyses; their percentages must not be applied to this baseline.

## Population and counting units

The export contains 4,557 unique MARC 001 records. It overlaps the original 3,946-record SRU harvest in 3,941 records; 616 are export-only and five harvest-only. The harvest used `sc.possessingInstitution = Z06 AND dc.date = YEAR`, for 1501–1525, at https://sru.swisscollections.ch/swisscollections. Z06 was too narrow for all ZB holdings. The 616 additional records have no Z06 holding.

The revised analysis includes 852 holdings coded Z01–Z06. UMWI is kept outside the ZB reference count. It yields:

| Measure | Count |
|---|---:|
| Export records retained | 4,557 |
| Catalogue copy references (record + institution + shelfmark) | 5,303 |
| Distinct institution/shelfmark pairs | 5,283 |
| Records with more than one ZB reference | 558 |
| Records without a Z01–Z06 852$j reference | 12 |
| Records with core provenance indicators, before exclusions | 1,226 |
| References whose record lacks core provenance indicators | 3,953 |
| Records flagged as microforms or later reproductions | 161 |
| ZB references in flagged records | 159 |

These are not counts of verified physical originals. The 12 records without a ZB shelfmark in 852$j remain in records.json; missing shelfmarks and non-ZB holdings require separate treatment. Reproduction flags are not deletions. The 161 and 159 counts refer to different units and populations.

| Holding code | References |
|---|---:|
| Z06 | 4,679 |
| Z03 | 475 |
| Z01 | 116 |
| Z02 | 30 |
| Z04 | 1 |
| Z05 | 2 |

## Exemplars and provenance

A reference is a distinct tuple of MARC 001, 852$b and 852$j within a record. Repeated identical tuples are collapsed. Shared shelfmarks across different title records are not merged: they can represent bound-with prints. The count of distinct shelfmarks is therefore not a substitute for the number of print copies.

Core indicators are public 561/361 and former-owner 700/710/711 entries (`fmo` or explicit former-owner terms). This is not an exhaustive interpretation of 563/590 or other notes. A lack of core indicators does not establish a lack of provenance evidence.

Every source field retains its subfields. Exact complete shelfmark matches in the same field's $3/$5 yield explicit candidate attribution. Composite scope expressions stay unresolved. Where one ZB reference and no other institutional holdings exist and the field has no scope qualifier, attribution is marked as an assumption. Other scope cases remain unresolved; they do not remove the reference from the population. No provenance is propagated between neighbouring fields. A candidate attribution is not yet a dated geographical station.

## Concrete checks

- 991124188289705501, Martialis (1501): both `4.330,2` and `V S 220` retained.
- 991000347729705501, Oratio (1512): Z03 `Ms S 3a,76` now included.
- 991019857919705501, Plinius (1508): 561 and 710 explicitly reference `4.305`.
- 991001556669705501, Corvinus (1516): `MFA 126` flagged by MARC microform encoding.

Validated record uniqueness, reference uniqueness, sums and these four examples against the source XML.

## Reproduction and date limitations

Automatic flags currently use microform 007/008 encoding and 008 type r with a reproduction year after 1525. This is a preliminary screen, not exhaustive exclusion. Hierarchical records, facsimiles described elsewhere, date ranges and the 12 records without a ZB reference still need automated assessment plus selected checks. No final percentage of original copies with provenance is claimed.

## Files and rerun

Run from the repository root:

```sh
python3 scripts/reconcile_postincunabula_export.py /path/to/2026-10-23-17h15.zip
```

No network calls are made. Outputs in `data/research/zurich-postincunabula-export-20261023/`:

- records.json: all export records, including those without a qualifying reference.
- copy-references.json: references, publication data and provenance coverage indicators.
- provenance-fields.json: original provenance subfields with attribution status.
- unresolved-holdings.json: ZB 852 fields lacking subfield j.
- summary.json: totals and limitations.

The next step is to assess original-print eligibility and remaining reference ambiguities, then extend provenance coverage beyond the core indicators. The map is unchanged.
