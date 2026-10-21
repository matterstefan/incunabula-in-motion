# Work plan

Initial plan, 21 October 2026. Steps are intended as manageable work sessions, without a fixed delivery deadline.

## 1. Identify the Zürich collection

Verify the current MEI holding-institution identifier and a supported search for the Zentralbibliothek Zürich. Inspect representative records and confirm pagination and scope. Distinguish current holdings from historical Zürich provenance in copies now held elsewhere. Record the query and retrieval date.

**Result:** a verified collection definition and a small sample for testing. Institution identifiers and query syntax remain to be checked; no identifier is assumed in this plan.

## 2. Adapt retrieval and data preparation

Reuse the existing retrieval and transformation code where appropriate. Select MEI records by current holding institution rather than by a thematic list of editions. Check which parts of the existing pipeline rely on the prayer-book corpus before reuse. Preserve MEI identifiers, source links, edition references and bound-with relationships without automatically transferring provenance between constituent prints.

Use resumable retrieval, caching and a shared request limit no higher than CERL's agreed maximum of 60 requests per minute. Confidential access configuration belongs in repository secrets, not source code. Confirm the applicability of existing access arrangements before substantially expanding retrieval beyond the pilot.

**Result:** a reproducible, dated Zürich export and a documented collection configuration.

## 3. Review geographical and chronological display

Reuse applicable reviewed place mappings with their provenance. Prepare only genuinely ambiguous cases for specialist review; city-level coordinates are sufficient. Retain uncertain dates and original wording. Areas must not silently become precise locality stops. Explain the convention of carrying the last recorded location forward between records.

**Result:** map-ready data, a review log and an explicit list of unresolved cases.

## 4. Adapt the interface

Reuse the established connection, circle and heatmap views, timeline, filters and session selection. Replace thematic collection controls with a library selector backed by collection configurations. Initially only Zürich needs to be available. Distinguish selection by current holding institution from historical provenance places.

Check that copy-level details retain institution, shelfmark, printing place and date, and links to original records. Test readability on a small laptop screen and performance with the full pilot collection.

**Result:** an independently deployable Zürich prototype. Prayer Books in Motion continues as its own project.

## 5. Evaluate transfer to another library

Invite a second interested library only when a working pilot is available. Measure what can be reused and which mappings or exceptions need new review. Discuss attribution, updates and responsibility for maintenance before presenting the application as an ongoing service.

**Result:** evidence for deciding whether to expand and how to maintain the shared code. Harvesting all MEI records is a possible later direction, not a prerequisite or current commitment.

## Working principles

- Keep source records and display corrections separate.
- Prefer documented catalogue identifiers over matching names alone.
- Do not count missing MEI records as evidence of missing historical holdings.
- Use the repository to record decisions, known limitations and future ideas.
- Consider a shared mapping component once a second application demonstrates which functions are truly reusable; avoid premature restructuring.
