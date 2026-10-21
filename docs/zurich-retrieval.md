# Zurich retrieval

The holding-institution identifier ZurichZB is evidenced in the existing MEI export, for example record 02129563. The proposed field query is data.holdingInstitutionId:ZurichZB. Its behaviour against the live endpoint must be verified by the test run; the offline sample is not a complete Zurich collection.

## Run

1. Upload scripts/mei_client.py, scripts/fetch_library.py and .github/workflows/harvest-library.yml into this repository.
2. In Settings > Secrets and variables > Actions, create the repository secret CERL_USER_AGENT using the confidential value supplied by CERL. Secrets in the Prayer Books repository are not inherited.
3. In Actions, select Retrieve Zurich MEI holdings and Run workflow with mode test.
4. Inspect the result artifact zurich-mei-results. The test contains up to five records and a server-reported total, not a complete collection.
5. If the test is successful and its records and reported total are plausible, run mode full. It retrieves all pages, verifies stable totals, distinct record counts and the current holding institution.

Do not run another CERL retrieval in the other repository concurrently. This workflow has repository-local concurrency control; its two-second spacing does not coordinate other repositories.

## Outputs

- zurich-test.json or zurich-full.json: complete returned source records, retrieval date, query and completeness flag.
- summary.json: mode, reported hit count, retrieved copies, distinct linked ISTC identifiers and subject coverage.
- subjects.csv: original subject/keyword terms, source fields and counts of distinct copies and editions. A copy appearing under the same term in both fields is counted once. Bibliographic terms are not new copy-specific classifications.

No public webpage or catalogue source is changed. GW enrichment follows separately using the October export. At this stage, a failed run must be restarted; persistent page checkpoints are not implemented. A changing hit count or duplicate/missing records causes failure instead of reporting an incomplete dataset as complete.
