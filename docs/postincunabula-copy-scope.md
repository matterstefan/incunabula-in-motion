# Copy-scope audit of Zurich post-incunabula

Offline audit, 23 October 2026. Bibliographic records with exposed holdings, not a census of physical items. Core scope: public 561/361 and former-owner 700/710/711. Binding and general copy notes are not exhaustively classified in this step.

| Classification | Field occurrences | Records (overlapping) |
|---|---:|---:|
| plausible_single_ZB_shelfmark | 1629 | 888 |
| unresolved_multiple_ZB_shelfmarks | 115 | 69 |
| explicit_shelfmark_in_scope | 50 | 25 |
| bound_volume_or_related_print_scope | 18 | 18 |
| unresolved_institution_or_scope | 20 | 9 |
| complex_scope_expression | 4 | 2 |

## Interpretation

Explicit means exactly one complete Z06 shelfmark string is found in subfield 3 or 5 of the same source field. It establishes a catalogue reference to that shelfmark, not a verified physical item ID. No scope is propagated to neighbouring fields or other owners. Single-shelfmark attribution remains an assumption; holdings from other libraries block it unless an explicit ZB institution scope is present. Narrative references and composite-volume mentions remain unresolved. Multiple statuses can occur in one record.

Matching is case/whitespace-normalised but otherwise conservative: variants and differing punctuation may be missed. Numeric prefixes must not match longer shelfmarks. Other institutional labels and complex qualifiers need further rules; no automatic map import follows.

## Examples of explicit scope

| Record | Field | Scope | Matched shelfmark |
|---|---|---|---|
| 991100053159705501 | 710 | Exemplar ZB Zürich; RRr 128,2 | RRr 128,2 |
| 991060302959705501 | 710 | Exemplar ZB Zürich; RRc 105 | RRc 105 |
| 991019857919705501 | 561 | Exemplar ZB Zürich (4.305) | 4.305 |
| 991019857919705501 | 710 | Exemplar ZB Zürich (4.305) | 4.305 |
| 991143400189705501 | 561 | Exemplar ZB Zürich (Gal St 561) | Gal St 561 |
| 991044751409705501 | 561 | Exemplar ZB Zürich; 4.361 | 4.361 |
| 991044751409705501 | 700 | Exemplar ZB Zürich; 4.361 | 4.361 |
| 991058757529705501 | 561 | Exemplar der Zentralbibliothek Zürich; Rm 145 | Rm 145 |
| 991058757529705501 | 710 | Exemplar der Zentralbibliothek Zürich; Rm 145 | Rm 145 |
| 991005215189705501 | 561 | Exemplar ZB Zürich (4.430) | 4.430 |

Spot check: compound scope “Signaturen Rs 800,3 und Rs 800; b,3” is explicitly withheld as complex even when one shelfmark matches. Literal matching alone must not silently discard an additional target. A full resolution of such expressions is deferred.
