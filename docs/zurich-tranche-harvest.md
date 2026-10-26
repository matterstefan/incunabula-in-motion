# Zurich tranche harvest (collector version 4)

## Current status: retrieval paused

Further Swisscollections catalogue requests and workflow runs are paused pending technical guidance from Swisscollections. Existing partial files remain useful for testing extraction, but are not a complete or representative census. See the [retrieval log and analysis plan](zurich-sru-status-and-analysis-plan.md).

## Scope and units

The collector queries `sc.possessingInstitution` for Z01–Z06 and an inclusive `dc.date` interval. Index matches can include manuscripts, reproductions and uncertain date ranges. Adjacent tranches may overlap.

A MARC 001 identifies a returned catalogue record. The derived profile additionally lists unique institution-code/shelfmark pairs from 852$b and 852$j. A reference is identified by record ID plus that pair; it is not automatically a distinct physical volume. Several references can share a record, and provenance in that record is not automatically attributable to every reference.

## Workflow and resumption

When retrieval is resumed by agreement, use the manually dispatched workflow in `.github/workflows/harvest-zurich-tranche.yml`. Inputs are start year, end year and snapshot label. Defaults are 1526, 1550 and 20261025. Do not start a run merely to test this documentation update.

The workflow restores cached pages for the same interval and snapshot label. It saves checkpoints and uploads the results artifact even after a failed collection step, where those steps can run. Artifacts are retained for 30 days. Download important results; workflow cache is not a permanent archive.

The collector:
- requests 100 records per page, sequentially, with at least two seconds between request starts;
- uses a 300-second request timeout and up to four attempts for transport errors;
- advances by the number of returned rows, including duplicates;
- deduplicates by MARC 001, retaining the first version;
- records conflicting repeated versions and preserves the raw pages;
- retains partial results on retrieval or parsing errors.

There is no 500-record-per-year selection limit. This implementation traverses up to the first 50,000 result positions for a query; larger result sets cannot be marked complete by this collector. The workflow allows 300 minutes for the collector and 350 minutes for the job, leaving time to save results. Neither limit establishes a recommended server load.

Using the same snapshot label reuses valid cached pages. A new label starts a separate cache. Reused and newly fetched pages do not form an atomic snapshot.

## Outputs

Under `data/research/zurich-tranches/{start}-{end}-{snapshot}/`:

| File | Meaning |
| --- | --- |
| `request-v4.json` | Query, endpoint, schema, page size and collector version |
| `pages/*.xml` | Successfully parsed MARC result pages |
| `diagnostics-v4/*.xml` | Returned response bodies, including responses that fail parsing |
| `retrieval-status.json` | Completeness checks, counts and any request error |
| `duplicates.json` | Repeated record IDs |
| `conflicting-records.json` | Repeated IDs with differing content |
| `record-profile.json` | Relevant fields and catalogue references for retrieved records |
| `summary.json` | Retrieval status, aggregate profile, page metadata and limitations |
| `progress.json` | Progress/checkpoint information |
| `failure.json` | Failure information, when an exception terminates the run |

A matching legacy `request.json` is accepted for cached pages. Responses lost before version 4 began preserving them cannot be recovered from a log alone.

## What “complete” means

`complete: true` requires traversal to finish, stable reported totals, a matching number of distinct IDs, no conflicting repeats and no request error. Even then, count verification cannot prove an atomic catalogue snapshot.

A transport or parsing failure saves the partial profile before the command exits with an error. Other incomplete or unverified results can finish with a warning and a successful exit code. **A green job does not establish complete coverage: read retrieval-status.json.**

## Initial profiling

Core provenance counts currently detect 361, 561, and former-owner entries in 700/710/711 identified by `fmo` or the supported role wording. These are record-level signals, not counts of verified provenance events or copies with geographic stations.

The profile retains additional contextual fields and review flags. Reproduction, material-type, date and missing-shelfmark flags are not automatic exclusions. Fields 361/541/561 with first indicator 0 are omitted from the derived profile; raw responses are preserved. This is not a general publication/privacy audit of all fields and subfields.

No biographical location inference, collection-history rules or manual owner enrichment is applied.

## Offline verification

Run:

```sh
python -m unittest discover -s tests -p test_zurich_tranche.py
```

The eight tests cover institution scope, checkpoint resumption, duplicate pages, changing totals, empty/invalid responses, conflicting versions and the distinction between references and record-level provenance. They use synthetic XML and make no catalogue requests.
