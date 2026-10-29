# Swisscollections retrieval status and next analysis

Status recorded on 25 October 2026. Retrieval is paused pending guidance from Swisscollections. This document consolidates the troubleshooting history reported during development; it does not constitute a fresh audit of every earlier artifact.

## Method update, 29 October 2026

The agreed [catalogue-density and provenance rules](marc-erschliessungsdichte.md) refine the analysis below. The primary counting unit is the catalogue record (MARC 001), not the shelfmark reference or physical volume. Fields are read together; multi-volume copy groups are not treated as multiple copies merely because they have multiple shelfmarks. The next step is offline calibration of content-based density categories on contrasting records. Retrieval remains paused. Existing scripts and historical counts have not been migrated to these rules.

## Retrieval history

| Attempt | Observation | Consequence |
| --- | --- | --- |
| Initial paginated collector | Duplicate IDs appeared across pages; a later replay of 2,000 returned rows yielded 1,962 distinct IDs. | Strict duplicate rejection stopped progress. Repeated IDs can be removed, but their removal does not recover potentially missing records. |
| Large single-response attempt | Parsing reported a missing SRU numberOfRecords element. The failed body was not retained by that version. | The cause cannot be established from that error; a server size restriction is not proven. |
| Adaptive partition proposal | A partitioning variant was prepared; no verified live result is documented here. | It is not evidence that partitioning solved retrieval. |
| Current version 4 | Partial profiling survives failures; duplicates and conflicts are logged. The latest reported attempt retained 1,900 cached records and timed out at startRecord 1901, against a reported total of 15,406. | No complete 1526–1550 dataset is established. The partial result is for technical testing only. |

Unstable ordering, catalogue updates, date-index overlap and service timeouts are possibilities to investigate, not interchangeable explanations or confirmed causes. Overlap between independently queried date intervals is expected to be deduplicated; repetition within paginated results additionally raises a coverage question.

The reported hit total is an index-selected record count, not a count of original printed copies. Material and date checks remain necessary.

## Questions awaiting Swisscollections guidance

- How should large result sets be paginated completely and with stable ordering?
- What page sizes, request intervals and runtime constraints are recommended?
- Are there relevant restrictions for GitHub-hosted runners?
- Is there a preferred automated export route and current technical documentation?

Reference: [SRU documentation](https://ub-basel.atlassian.net/wiki/spaces/swisscollections/pages/1974370315/SRU-Schnittstelle). The previously linked GitLab resource was not publicly accessible during troubleshooting; that does not establish that it has been deleted.

## Next analysis: what can existing data support automatically?

The aim is to measure what existing catalogue data make reusable, rather than to assess overall cataloguing quality by whether a map can be drawn. Start with the existing post-incunabula material to develop the method; use a sufficiently complete wider tranche before drawing collection-wide conclusions.

1. **Define the population.** Use distinct MARC 001 records as the analysis unit, with query, export date, retrieval status, exclusions and retained review cases documented. Keep older reference-based counts separate; volume counts are not required. State record denominators with every proportion.
2. **Inventory meaningful content.** Count non-empty provenance notes, owner entries, identifiers, roles, dates, places and explicit reference links. Separate simple field presence from usable content. Preserve source field, indicators, subfields and original wording.
3. **Read copy context.** Catalogue owner information remains usable for record-level analysis. Treat a described multi-volume copy group as a whole under the agreed working hypothesis, preserving the location of individual marks and explicit exceptions. Read 300, 852 and 949 together. Where genuinely separate copies occur, copy-specific attribution requires a clear owner–shelfmark link; do not mistake multiple volume shelfmarks for multiple copies.
4. **Assess entities and relationships.** Count persons and institutions with usable authority identifiers, explicit ownership roles and repeat appearances. Name-only mentions remain separate from securely identified entities. Shared owners do not establish contact between people, transfers between collections or chronological order.
5. **Assess temporal and geographic evidence separately.** Retain catalogue dates and places with uncertainty. An identified owner without a recorded place can still support a collection-history analysis. Label any lifespan-based bounds on personal ownership as biographical inference, not as recorded ownership dates or continuous possession. Do not infer a print's location from an owner's biography alone.
6. **Choose a demonstration from the results.** Depending on density and attribution, candidates include owner–copy networks, collection groupings, dated provenance sequences or geographic stations. A sparse map need not imply sparse historical information.

## Separate automatic reuse from enrichment

Previously reviewed owner identities, collection histories, shelfmark rules and externally inferred places must remain identifiable as enrichment. Report the catalogue-only baseline separately from any enriched version. Broadening chronological coverage should not silently depend on case-by-case manual review.

No additional live retrieval, manual owner research, map changes or deployment is part of this consolidation. Once guidance arrives, revise the retrieval strategy first, then run it through GitHub Actions and assess the resulting coverage.

## Consolidation checks

The version-4 collector, tranche workflow, tranche tests, tranche guide and README were inspected. The old resumption test expected a raised exception where version 4 intentionally returns a partial result, and the old guide described the earlier stopping policy. Tests and documentation have been aligned with the existing collector; its retrieval behavior has not been changed.

Eight synthetic offline tests pass. This verifies the tested local behavior, not Swisscollections service behavior or completeness of any live dataset.
