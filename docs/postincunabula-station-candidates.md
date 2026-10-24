# First provenance-place candidates for ZB postincunabula

24 October 2026. The current provenance-assignments.json and working-copy-context.json were recovered from the public project repository. Their 5,149-reference baseline and assignment summary match the previously reported totals. No new catalogue harvest was performed.

## Result

340 evidence-based place candidates concern 320 distinct catalogue references. This is a deliberately limited first pass, not the total number of localisable copies. 337 candidates have no assigned date; three have a year or relative date from reviewed notes. Multiple candidates may refer to one owner/event, especially where dated and undated fields overlap. Do not interpret the candidate count as a count of movements.

| Place | Distinct references (overlapping) |
|---|---:|
| Gosnay | 1 |
| Luzern | 23 |
| Rheinau | 234 |
| Zürich | 74 |

## Rules and confidence

Six already documented institution-locality rules are applied to assigned corporate former-owner fields by GND. Their sources are retained. Four reviewed records contribute the Orelli donation and biographical inference, probable Hagenbuch identity, explicit Gosnay note and Rheinau 949 note. Source wording is preserved; explicit/plausible copy linkage and inferred/explicit place evidence remain separate.

The Biel/Pellikan case remains unresolved. No automatic rule maps every Zwingli, Gessner or Simler ownership to Zurich. Their biographical proposals remain separate. Neither life dates nor institutional foundation dates are inserted as copy dates. The Zwingli museum context is not converted into an individual dated event.

The existing 45 reproduction-review references remain part of the baseline; this step introduces no further exclusions. No geocoding, ordering, interpolation or map update is performed.

## Example date treatment

- Plinius 4.305: Stadtbibliothek Zürich, donation in 1839; Orelli in Zurich immediately before that donation is a separate reviewed inference.
- Plautus 4.221: inscription dated 1753; identity and Zurich location probable.
- Gosnay and Rheinau: no date assigned where the selected source does not supply one.

## Reproduce and resume

Run `python3 scripts/build_postincunabula_station_candidates.py`. It reads the restored provenance assignments, working copy context and existing institution-locality authority table. Outputs station-candidates.json, station-candidate-summary.json and station-unlocated-evidence.json. The last file contains linked source fields without an applied rule, not a list of distinct unknown places.

Next: interpret repeated free-text owner notes and review person/collection locality proposals; reconcile duplicate evidence for the same event before building a timeline. Original printed place and current holding are not duplicated here: this file concerns historical intermediate provenance only.

Validation: all target keys exist in the baseline; no candidate attributed to the unresolved Biel groups; the reviewed Rheinau 949 note is not propagated to Res 915.
