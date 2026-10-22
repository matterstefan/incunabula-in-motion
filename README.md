# Incunabula in Motion

An exploratory project for visualising the provenance and circulation of individual incunabula copies recorded in Material Evidence in Incunabula (MEI).

The project builds on the mapping application developed for [Prayer Books in Motion](https://matterstefan.github.io/prayer-books-in-motion/). The initial Zurich prototype has been extended to 3,394 MEI copy records from 21 Swiss holding institutions (snapshot: 22 October 2026). Individual libraries can be selected separately or together.

## Purpose

Incunabula in Motion aims to make existing catalogue data accessible through maps, timelines and copy-level exploration. It is intended to support discovery, research questions and the communication of cataloguing work. It does not reconstruct complete journeys or constitute a new bibliographical catalogue.

## Data and scope

- MEI will provide copy identifiers, holding information and provenance records.
- Edition information, including printing places and dates, will be reused from linked catalogue records where available. ISTC and GW links will be retained where supplied or verified.
- The unit of exploration is an individual copy of a printed edition, not necessarily a present-day bound volume.
- Printing places form the starting points and current holding locations the endpoints where these are known. Recorded provenance stations fall between them; missing locations or dates will not be invented.
- Original source values will remain distinct from documented decisions made for geographical display.
- A library view will represent its selected MEI records, not necessarily its complete incunabula holdings. Coverage and retrieval dates will be stated.

The current scope is the Swiss holding institutions represented in the supplied MEI snapshot. This does not imply complete coverage of Swiss libraries or their holdings. See the [Swiss collection preparation and review notes](docs/swiss-collections-20261022.md).

## Status

Swiss collections update, 22 October 2026. The map includes library, subject, printing-place and language filters, a historical timeline, connections, circles and a heatmap. See the [work plan](docs/work-plan.md) and [reproduction instructions](docs/swiss-collections-20261022.md).

## Access and maintenance

Data retrieval will run separately from the public website, with deliberate refreshes and dated exports. Automated access must respect CERL's agreed access conditions and request limits. Access credentials and any confidential access configuration must never be committed to this public repository.

This is an independent project, not an official CERL service. Source attribution and links back to the catalogues are central to the design. Code licensing and the reuse conditions applicable to individual data sources will be documented separately.

## Project lead

Stefan Matter. Developed from the experience of Prayer Books in Motion within PRAYTICIPATE; this new project has a broader collection-based scope. Institutional participation or endorsement will only be stated when agreed.

## Zurich map prototype

The first map is available from the repository-root `index.html` once GitHub Pages
is enabled. See [first-map.md](docs/first-map.md) for preparation, deployment and
known limitations. The UI includes the timeline, connections, circles, heatmap,
MEI subject/keyword filters, languages, printing places and saved selections.
