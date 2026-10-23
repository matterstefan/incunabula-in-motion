# Zurich post-incunabula retrieval

Run **Actions → Collect Zurich post-incunabula → Run workflow**. No secret required: this uses the public swisscollections SRU service, not CERL. Results are uploaded as `zurich-postincunabula-results`, including checkpoints after failures. Completed year responses are reused from the repository or Actions cache. This is a manual snapshot, not a scheduled update; rerunning does not refresh saved years.

Scope: Z06 (ZB Alte Drucke und Rara), indexed dates 1501–1525. Each year must arrive in one complete response, maximum 500 records. Queries run sequentially. Duplicate identifiers across years are counted once. If a year exceeds the limit, the script stops rather than silently truncate. Review date statements and copy identity before treating results as physical post-incunabula.

The included snapshot has 3946 distinct records from 25 complete year responses. The broader date-range query gave 3969: the additional 23 records are saved in range-only.xml for review and include modern reproductions. The date index is therefore not equivalent to the printing date of the physical item. An additional 26 records in the year-query set have a first 008 date outside the period or not numeric and require review.

Preliminary record-level counts: 496 with public 561; 929 with former-owner access points; 901 with authority identifiers on former-owner access points; 997 with 561/361 or former-owner access points combined. No 361 found. These are not yet counts of geolocated stations or unique copies. 563 and 590 require content interpretation. A record can contain multiple holdings and notes whose copy scope needs checking.

The workflow writes no commits and does not change the live map. Download and retain the result artifact. The supplied source script and workflow are ready to place at the corresponding repository paths.
