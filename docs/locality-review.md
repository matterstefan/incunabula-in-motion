# Zurich locality review — 21 October 2026

Run `python scripts/prepare_zurich.py`, then `python scripts/review_zurich_locations.py`.
The latter produces `stations-reviewed.csv` without overwriting either the raw
snapshot or the earlier station tables. This is a preparation stage, not a map release.

All nine multiple GW matches agree on their printing place. Their titles and date
statements remain separate. The review uses the shared place for coordinate lookup;
it does not choose a GW record or supply a date from another candidate.

284 previously unlocated stations match existing city vocabulary entries exactly
(including explicitly stored name aliases). Source labels and coordinate references
are retained. Explicit GW `[vielmehr: ...]` corrections may supply the lookup name;
question marks and alternative places are not silently removed.

386 stations still lack coordinates. These are not 386 scholarly questions:
`locality-review-triage.csv` separates ordinary technical lookups, source uncertainty,
multiple production places, regions and missing localities. Coordinates already
present in MEI have not undergone a comprehensive historical validation here.

One identified question for Stefan: MEI 02129584, shelfmark Ra 20, contains the
ownership note “Sum parochiae Seefeldensis”. Which Seefeld parish is meant? The later
Rheinau provenance alone does not establish this.

For the two Vienne printing-place records, MEI 00570713 and 00570672, the host-item
country code is FR. Thus the source specifies French Vienne, not Vienna. Coordinate
lookup remains to be completed.

Paris and Bourges, and Reggio Emilia and Bologna, are multiple production-place
statements; they must not be transformed into an inferred sequential journey.
Regional and unknown-place records remain in the data without city coordinates.

Next: complete technical city lookups with source context (especially bare Freiburg,
Burgdorf and Rougemont), review uncertain printing-place/date statements, and only
then build the map input. Do not interpret this triage as completed geolocation.
