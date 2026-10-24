# Reconstructed dated MARC pilot — 24 October 2026

This package rebuilds a conservative pilot from the retained ZB Zürich catalogue
references and their assigned provenance fields. It does not modify the website.
It is not a byte-for-byte recovery of the earlier lost package; identical totals
alone do not prove identical membership.

## Result

- 5,149 catalogue references in the working corpus.
- 31 selected references with a dated institutional event and a resolved publication locality.
- 93 station objects: publication, one selected historical event, current holding.
- Historical event precision: 28 exact years, two circa 1540, one probable 1832.

A reference is the combination of bibliographic record ID, institution code and
shelfmark. These are not independently verified distinct physical volumes. Some
references describe bound-with prints or multiple volumes. Never report 31 as
the total number of copies with usable provenance. Earlier place candidates,
collection-based enrichment and undated evidence remain unchanged in the project.

## Selection and limits

The script recognises a small, explicit set of wording patterns for dated donations
to Stadtbibliothek Zürich, Pellikan's donations to the Grossmünster library, and a
dated dedication to the Naturforschende Gesellschaft Zürich. It accepts only
previously explicit or plausible copy assignments, preserving that distinction.
It never uses a desired output count, personal lifespans or institutional founding
dates to supply event dates. A year near a library stamp is not sufficient.

The purchase at Vienna in 1517 and the gift to Stadtbibliothek Zürich in 1780 can
occur in the same note: this pilot selects the **1780 gift**, not the purchase.
This is a deliberately incomplete sequence. Caspar Orelli in that 1780 note is not
identified as Johann Caspar von Orelli born in 1787. The recipient institution is
the geographical anchor; no donor biography is inferred.

The related references `991041866759705501` and `991136341899705501` are held for
review: the notes distinguish donation in 1836 from a donor-register entry in
1838. These may be different events rather than contradictory dates. They are not
silently reduced to one year. Other notes outside the narrow rules are retained
in `route-pilot-unparsed-dated-notes.json`; this includes potentially useful
material, not rejected or disproved provenance. For example, the Hans Wilhelm
Wolf note of 1629 falls outside the implemented wording patterns and its
publication statement names both Paris and Cologne.

The first anchor uses MARC 008's single-year publication code and the original
260/264 wording. It does not establish a separate physical printing place where
the catalogue statement concerns publication/distribution. Source brackets and
original date strings are retained. Publication place normalisation is an exact,
reviewable label mapping, not a generic geocoder. Multiple or unknown places
are left pending rather than converted to one point.

Current holding is observed at the catalogue export date, **23 October 2026**.
It is not the acquisition date. Circa/probable historical years must remain
qualified when these data are integrated into the time slider. None of the three
anchors establishes uninterrupted residence or a continuous journey.

## Files to inspect

Open `data/research/zurich-postincunabula-export-20261023/route-pilot-review.html`
in a browser for a readable list with catalogue links and original MARC notes.

The same directory contains:

- `route-pilot-geocoded.json`: routes with sources, assignment confidence and coordinates.
- `route-pilot-summary.json`: counts and input SHA-256 hashes.
- `route-pilot-review.json`: linked references requiring date interpretation.
- `route-pilot-pending.json`: event cases lacking a usable publication anchor (currently empty).
- `route-pilot-unparsed-dated-notes.json`: other assigned notes containing year tokens, without automatic event interpretation.
- `route-pilot-controlfields.json`: MARC 008 snapshot from the original export, including records outside the selected pilot.

Coordinate provenance is recorded per station. Most points reuse the project's
existing GeoNames/MEI authorities. Oppenheim uses the Getty TGN inhabited-place
point, ID 7012639: https://www.getty.edu/vow/TGNFullDisplay?english=Y&find=&nation=&place=&subjectid=7012639
This identifies a town, not a building.

## Reproduce offline

From the repository root, using Python 3 (no extra packages):

```sh
python3 scripts/prepare_postincunabula_route_pilot.py
python3 -m unittest discover -s tests -p 'test_postincunabula_route_pilot.py'
```

The package includes the two existing source snapshots required for reproduction:
`working-copy-references.json` and `provenance-assignments.json`, as obtained from
the public project repository on 24 October 2026. Their hashes are in the summary.
No live catalogue access or CERL secret is needed.

If the original swisscollections export is available, the control-field snapshot
can also be recreated:

```sh
python3 scripts/prepare_postincunabula_route_pilot.py --export-zip /path/to/2026-10-23-17h15.zip
```

For a genuinely new catalogue snapshot, regenerate the working references and
provenance assignments with the upstream project scripts as well; refreshing
008 alone does not constitute a corpus refresh.

## Installation

Copy the contents of this package into the existing repository, preserving
`scripts/`, `tests/`, `docs/` and `data/`. Existing source snapshots in this package
are unchanged copies of the retrieved versions. Check GitHub Desktop's changes,
commit and push. Suggested commit message:

`Restore reproducible dated MARC route pilot with source evidence`

The map integration is a subsequent step. No frontend files are replaced here.
