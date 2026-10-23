# Reproduction screen of the all-ZB export baseline

23 October 2026. Offline analysis; the original export and baseline are unchanged.

## Result

Of 5,303 catalogue copy references, 154 are excluded from the working set: 129 microform references and 25 references to later reproductions. These belong to 149 source records. The working set retains 5,149 references in 4,396 source records. These are candidate historical-copy references, not a verified count of physical originals.

45 references are retained for review: 40 have electronic encoding without an explicit physical carrier, and five have mixed physical/microform descriptions. The 12 baseline export records without a qualifying ZB 852$j remain separately available in records.json; they were never part of the 5,303 reference count.

The earlier 161 flagged records and 159 flagged references were screening candidates. They were not exclusion totals. The final rules retain five of those references because their mixed carrier descriptions require context.

## Rules and evidence

- Microforms: MARC 007 starts with h, or 008 position 23 is a/b/c, or an explicit microform 338$b. If a physical carrier nc/nb is also present, exclude only the reference with an MF-style shelfmark; otherwise retain for review.
- Later reproduction: 008 date type r and first date after 1525. Preserve the complete 008 as evidence. The reproduction date is distinguished from the original publication date.
- Electronic encoding never causes automatic exclusion. Original prints and their digital surrogates may share one record. 419 retained references have electronic encoding.
- Fields 533/534 are preserved for context. A note alone is not used to exclude a reference without the above evidence.
- No additional date-range, hierarchy, original-edition or shelfmark-identity decisions are introduced in this step.

## Files

In data/research/zurich-postincunabula-export-20261023:

- working-copy-references.json: retained references, including review cases.
- excluded-reproductions.json: every excluded reference with rule and source evidence.
- reproduction-review.json: retained ambiguous cases.
- reproduction-summary.json: totals.

Rerun after generating the baseline:

```sh
python3 scripts/screen_postincunabula_reproductions.py /path/to/2026-10-23-17h15.zip
```

## Validation

Checked conservation of all 5,303 reference keys and disjoint inclusion/exclusion sets. Corvinus, MFA 126, is excluded as a microform; the 1882 lithographic reproduction of the papal banner print is excluded; both references to the 1963 Missale reproduction are excluded. Wimpfeling, Ra 35,19, remains despite its additional electronic carrier encoding.

No map changes or new catalogue requests are included. Provenance coverage percentages should await the remaining baseline review.
