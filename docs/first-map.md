# First Zurich map — 21 October 2026

The static frontend adapts Prayer Books in Motion for the Zurich institutional
selection: 1,609 distinct MEI copy records, with 8,778 source station rows.
8,734 station rows have usable local coordinates after the current preparation.
These counts are not counts of unique cities or independently documented journeys.

## Rebuild offline

From the repository root:

```sh
python3 scripts/prepare_zurich.py
python3 scripts/review_zurich_locations.py
python3 scripts/build_zurich_map.py
node tests/zurich-map.cjs
```

Use the existing source snapshots. None of these commands contacts CERL.
The new map reads `data/map/`, not the earlier preparation tables directly.
`data/authority/zurich-locality-decisions.json` records selected GeoNames points,
identification evidence and the deferred Seefeld question.

## Decisions and limits

- Ordinary outstanding city lookups are completed using selected GeoNames records.
- Freiburg is Freiburg im Breisgau, explicitly confirmed in MEI imprints.
- Vienne is the French city, confirmed by both relevant host-item country codes.
- Burgdorf and Rougemont are Swiss printing places despite the embedded country
  codes. Evidence is linked in the decision file.
- Seefeld, MEI 02129584, remains unlocated. Stefan will ask the Zurich cataloguers.
- Four Zurich label/coordinate conflicts are suppressed from map geometry, with
  original data retained. Three are the previously noticed Iran points; the
  fourth is another inconsistent coordinate. See `map-review-issues.csv`.
- Dates are checked for reversed ranges and provenance predating the printing
  anchor. Flagged events remain in present-day details but do not anchor the
  historical timeline. Eighteen issue rows concern dating (some stations have
  more than one issue); this is not an expert revision of all catalogue dates.
- Approximate GW dating uses the normalised year as an explicitly qualified
  display anchor. Original GW date statements appear in station details. Multiple
  GW candidates retain their statements; differing normalised years remain
  unassigned rather than selecting a candidate arbitrarily.
- Multiple/alternative printing places and unidentified regions are not turned
  into single local points or invented travel sequences.
- Current holding and immediately preceding provenance at the same point are
  compacted only in the presentation; source rows remain separate.
- Subjects/keywords come from MEI's embedded bibliographic fields. Case and spelling
  variants are retained; counts beside subject options refer to the whole Zurich
  collection. Subject choices use OR, and combine with other filters using AND.
- This first version does not yet import digitisation links or offer a selector
  for further libraries. It is a Zurich prototype, not an all-MEI release.

## Open and publish

Copy the update contents into the existing repository, preserving folder paths,
then commit and push. The site entry point is `index.html` in the repository root.
GitHub Pages must be configured to serve that root from the main branch, or an
existing deployment process must publish `index.html`, `assets/` and `data/map/`.
This update does not add a deployment workflow or alter the harvest workflow.

For a local preview, serve the repository with a static web server (for example
`python3 -m http.server 8000`) and visit `http://localhost:8000/`. Opening the HTML
file directly is insufficient because the browser must load the CSV files.

## Validation

Browser checked: full initial dataset, source-term filter, Connections, Locations,
Heatmap, year 1600, copy details. Automated checks cover all 1,609 detail views,
current holdings, pre-printing timeline exclusion, flagged dates, suppression of
Iran conflicts, unlocated Seefeld, subject OR/language AND and saved searches.
Raw source snapshots were not modified. No comprehensive historical validation of
all source coordinates or dates is claimed.
