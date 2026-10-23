# Item context and reviewed provenance decisions

23 October 2026. This update supplements the field inventory without changing the map or the number of retained catalogue references.

## 949 association

The script attaches 949 occurrences to retained references only when record ID, institution code (949$b) and shelfmark (949$j) match exactly. Original subfields, additional shelfmark strings ($h), part labels ($q) and notes ($z) are preserved. Record-level 019 and 300 descriptions are also retained. No occurrence is automatically equated with a physical copy and no group is split or merged.

| Measure | References |
|---|---:|
| Retained baseline | 5,149 |
| With matching 949 context | 4,902 |
| With multiple matching 949 fields | 167 |
| With part labels in $q | 252 |
| With notes in $z | 2,852 |

Notes include routine service information; 2,852 is not a provenance count. Three 949 occurrences in the examined records have no exact retained-reference match and remain separately documented. The 45 reproduction-review references remain included.

## Reviewed examples

The case decisions are preserved in review-decisions.json. Orelli's Zurich location just before the 1839 donation is a biographical inference. Hagenbuch's identification and Zurich location in 1753 remain probable. The original catalogue wording is not replaced. These are case-specific decisions, not rules assigning every book of an owner to every place in that person's biography.

Uncertain Zwingli ownership remains uncertain. Gosnay is an explicit place without an invented date or sequence. The Rheinau note is attached only to RRr 125 through its own 949 field. Binding decoration alone is not an ownership event.

For Biel (991001105039705501), retain both reference groups and all four 949 occurrences. IV S 61 and IV S 62 have part labels 1-2 and 3-4; the physical arrangement and the Rm group are not conclusively determined. The Pellikan donation note remains unassigned to a group. The label Unikatsaufnahme is retained without treating it as an exemplar count.

For Zwingli 243, the Handbuch shelfmark table and section 2.62 provide museum/collection context, not proof of Zwingli's personal ownership or a specific acquisition date.

## Rerun and outputs

```sh
python3 scripts/enrich_postincunabula_item_context.py /path/to/2026-10-23-17h15.zip
```

Reads working-copy-references.json. Writes working-copy-context.json, item-context-summary.json and unmatched-item-context.json in the same data directory. The separately maintained review-decisions.json records the scholarly decisions and is not overwritten by the script.

Validated reference-key uniqueness and unchanged count; checked all four Biel occurrences and verified that the Rheinau note does not propagate to Res 915.
