# Optional MARC map pilot — 24 October 2026

The map now loads `data/map/marc-pilot.json` alongside the unchanged MEI CSVs.
The source remains the reconstructed, source-linked pilot; the JavaScript adapter
creates display records without manufacturing MEI or ISTC identifiers.

## User behaviour

- MEI remains selected by default (3,394 references).
- A second checkbox enables 31 ZB postincunabula MARC references, alone or alongside MEI.
- Dataset choices use OR; the library, language, publication-place and search filters combine with them using AND.
- MARC records share the existing `ZurichZB` holding filter.
- MARC language comes from the exported 008 field; no extra multilingual enrichment is inferred.
- MEI subject filters exclude MARC records, which have no MEI terms.
- Reset returns to MEI only. Saved selections retain explicitly added copies, as before.
- The detail panel links to swisscollections and quotes the source MARC note and copy-assignment qualification.
- Historical Zürich and present holding remain distinct in the station list even at identical coordinates.
- Two circa 1540 dates and one probable 1832 date retain their qualifications. The slider uses those years as approximate anchors, not newly established exact dates.
- Publication wording and the original date string remain visible. Current holding in 2026 is not dated acquisition.

The adapter retains the existing technical `print_place` type for the first anchor
so route and filter logic remain compatible. Its MARC detail label explicitly says
“Publication place (catalogue statement)”. This does not independently establish
the physical printing location. These are selected institutional anchors, not
complete provenance sequences and not all usable provenance in the corpus.

## Installation and regeneration

Copy package contents into the repository and commit normally. Both root and
`dist` assets are supplied, with versioned JS/CSS references to refresh browser caches.
The previous reconstruction package contains the authoritative research inputs.
After regenerating the pilot, run:

```sh
python3 scripts/publish_marc_pilot.py
node tests/swiss-map.cjs
node tests/marc-map.cjs
```

Tests cover the existing 3,394 MEI references, the 31 MARC references / 93 stations,
dataset combinations, filters, catalogue-ID searches, distinct IDs, approximate
years, current holding and source-linked detail rendering. Browser visual checking
was unavailable in the execution environment; layout should be reviewed on the
user's usual small screen after deployment.

Suggested commit: `Add optional ZB MARC pilot collection to the map`
