# Additional dated MARC events — prepared, not published

24 October 2026. This is a separate preparation tranche, not a map replacement.

## Result

The script extracts 19 dated event candidates across 19 catalogue references:

- Eight Vienna purchase records dated 1517 add an earlier anchor to references
  already in the first pilot. The later gift to Stadtbibliothek Zürich in 1780
  is a different event. The shared note does not establish eight separate
  transactions or the binding history of the constituent prints.
- Seven Rheinau events, two Lucerne events, and two Zürich events concern eleven
  references outside the first pilot.

This would extend the pool from 31 to 42 references if all eleven new references
are subsequently prepared as routes and accepted for display. The eleven do not
yet have a complete, checked publication-to-current-holding route in this tranche.
No new data have been added to the map by this package.

## Evidence and limits

Only already explicit or plausible copy assignments are eligible. Each candidate
retains the full MARC field, target shelfmark, source URL, exact matched wording,
year, owner/institution and extraction rule. Full notes remain available even when
the extraction selects only one event. These are catalogue references rather than
a count of independently verified physical volumes or transactions.

A date attached to a different owner is not assigned to a nearby institutional
stamp. Personal lifespans are excluded. No generic place is inferred merely from
a person's surname or origin. An inscription on a bound-with print remains indirect
evidence for other constituents: it does not establish when they were bound together.

Coordinates reuse the existing MEI/project authority points for Vienna, Rheinau,
Lucerne and Zürich; each point records its source. Institutional locations are
analytical locality assignments, not building coordinates.

## Inspect and reproduce

Open `data/research/zurich-postincunabula-export-20261023/additional-dated-events-review.html`
in a browser for the readable source list. JSON files contain the same candidates
and a summary with hashes of the input snapshots and rules.

From the repository root:

```sh
python3 scripts/prepare_additional_marc_events.py
python3 -m unittest discover -s tests -p 'test_additional_marc_events.py'
```

This package includes the required unchanged reference/assignment inputs and the
first-pilot map snapshot for comparison, so it can be reproduced offline. Rules
are in `data/authority/postincunabula-additional-event-rules.json`. No CERL access
or confidential request header is required.

Next: review the eleven new references' publication statements and years, prepare
their endpoints, and explicitly retain bound-with scope in the map details. The
eight Vienna anchors can then be added to the existing routes as separate events.

Suggested commit: `Prepare additional dated MARC provenance events`
