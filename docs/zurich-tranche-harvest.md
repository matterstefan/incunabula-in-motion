# Automated Zurich date-tranche assessment

## Purpose and change of direction

The question is how much usable provenance information the existing catalogue exposes automatically across larger Zurich populations. Manual owner research and collection-based location inference remain separate experiments. They are not used by this collector. The website and earlier datasets are unchanged.

Start with 1526–1550; subsequent runs can cover 1551–1575 and 1576–1600. A new 1501–1525 run is possible later to establish a directly comparable automated baseline, but is not required now. Earlier export-based counts and this SRU profile are not interchangeable without reconciliation.

## Upload and run

Copy the four package files to their matching repository paths, commit, and push. This is an additional package: keep the previously downloaded packages too; it does not replace them.

Suggested commit: `Add resumable Swisscollections harvest for Zurich date tranches`

In GitHub select **Actions → Collect Zurich date tranche → Run workflow** on the branch containing the new workflow (normally main). Defaults:

- First year: `1526`
- Last year: `1550`
- Snapshot: `20261025`

No CERL secret is needed. The script uses Swisscollections, not MEI. It does not commit results or deploy the map. Download `zurich-tranche-1526-1550-20261025` from the completed run's Artifacts section.

Keep the same dates and snapshot label to resume an interrupted run. Completed pages are cached; they are not queried again. Change the label for a genuinely fresh snapshot. Cache eviction is possible: if no checkpoint survives, the workflow retrieves the pages again. Artifacts are retained for 30 days and should be downloaded.

## Retrieval and completeness

The query includes Z01–Z06, the institution codes used for the revised Zurich baseline. It uses a date-range query directly rather than a union of individual-year searches. This avoids silently dropping range-only matches. It does not add an unverified format or hierarchy filter: non-print records, reproductions and uncertain dates are retained and flagged for subsequent assessment.

SRU responses are requested sequentially in pages of 100 with at least two seconds between request starts. The collector checks MARC 001 uniqueness, SRU diagnostics, hit-count consistency, empty pages and the final count. Each checkpoint has its request URL and SHA-256 hash. A stable hit count cannot guarantee a fully atomic catalogue snapshot; this limitation remains explicit.

Swisscollections documents a retrieval ceiling of 50,000 records. The script stops if the query exceeds it; choose a smaller date interval. It never treats the first 50,000 as a complete harvest.

The retrieval has a five-hour process limit within a 350-minute job, leaving time to save checkpoints and upload partial results. A failed/partial run is not a completed dataset. `progress.json` and `summary.json` identify completion; `failure.json` records ordinary errors. Timeout may leave only the progress file. Do not run the older Swisscollections collector simultaneously with this one.

Documentation consulted 25 October 2026:
https://ub-basel.atlassian.net/wiki/spaces/swisscollections/pages/1974370315/SRU-Schnittstelle

## Outputs and counting levels

- `pages/*.xml`: original public SRU responses, including all MARC fields returned.
- `request.json`: query configuration.
- `progress.json`: checkpoint progress/completion.
- `summary.json`: counts and limitations after a complete run.
- `record-profile.json`: titles, ZB shelfmark references, publication fields, provenance/other note fields and scope subfields.
- `failure.json`: error information when applicable.

The initial profile reports records containing public 361/561, former-owner access points, owner authority identifiers and other candidate note fields. Tags 541, 563 and 590 are measured separately and do not by themselves establish historical provenance. Empty fields can contribute to field-presence counts; subsequent assessment must examine their content.

A catalogue reference is MARC 001 + institution + shelfmark. Several references can belong to one record. The count `references_in_records_with_core_provenance` is deliberately NOT a count of copies with assigned provenance: it indicates references in records containing such fields. Source fields and their $3/$5 scope qualifiers remain available for later attribution. An owner authority identifier does not establish a geographical station.

Microform encodings, reproduction date type, out-of-range/uncertain first 008 dates, non-language-material coding and missing ZB shelfmarks are review flags, not deletions. Language material is not equivalent to an eligible original printed item. Overlap between adjacent date tranches is possible and must be measured using MARC IDs/reference keys before adding totals.

Private-indicator 361/541/561 are omitted from the derived profile; raw public endpoint responses are retained in the artifact. Do not publish the raw artifact indiscriminately. Public map data will be a separately prepared subset.

## Next automatic analysis

After retrieval, establish the eligible reference population and field-to-reference attribution, using the same rules across tranches. Report separately: field presence, assignable provenance, directly supplied location evidence, usable dates and geolocatable stations. Preserve unresolved data and the reasons for non-use. Do not apply biographical or handbook enrichment to the automatic baseline. A low yield is a result, not a reason to silently expand the inference rules.

## Validation

Five offline tests cover all six institution codes, pagination and checkpoint resume, duplicate/changing counts, zero results/the retrieval ceiling, and separation of private fields and record/reference counts. No new live catalogue harvest was run in ChatGPT. The first GitHub run also serves as the live check of the combined range query.

Run tests: `python -m unittest discover -s tests -p test_zurich_tranche.py`
