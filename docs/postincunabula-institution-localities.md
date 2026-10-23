# Institutional locality pilot — Zurich post-incunabula

23 October 2026. Offline reuse of explicit former-owner access points. No shelfmark-based provenance inference and no new catalogue requests.

Six rules cover 335 distinct bibliographic records; 32 have multiple Z06 shelfmarks and unresolved allocation of notes to copies.

| Institution | Locality | Records | Source |
|---|---|---:|---|
| Kloster Rheinau | Rheinau | 253 | Handbuch der historischen Buchbestände in der Schweiz, vol. 3, Zentralbibliothek Zürich, §1.16–1.20, pp. 368–369 |
| Stadtbibliothek Zürich | Zürich | 34 | Handbuch der historischen Buchbestände in der Schweiz, vol. 3, Zentralbibliothek Zürich, §1.21–1.22, p. 369 |
| Jesuitenkolleg Luzern | Luzern | 23 | Explicit locality in the catalogue corporate-owner name Jesuitenkolleg Luzern; authority identifier used for identity matching, not externally fetched |
| Großmünster | Zürich | 21 | Handbuch der historischen Buchbestände in der Schweiz, vol. 3, Zentralbibliothek Zürich, §1.2, p. 365 |
| Kantonsbibliothek Zürich | Zürich | 11 | Handbuch der historischen Buchbestände in der Schweiz, vol. 3, Zentralbibliothek Zürich, §1.87–1.88, p. 380 |
| Naturforschende Gesellschaft in Zürich | Zürich | 11 | Handbuch der historischen Buchbestände in der Schweiz, vol. 3, Zentralbibliothek Zürich, §1.1, p. 365 |

## Interpretation

Counts overlap between institutions. These are locality assignments to named institutional former owners, not dated copy movements. The catalogue supplies the ownership relationship; the handbook or explicit institutional name supplies the locality. No institutional founding date, dissolution date, transfer date or predecessor chain is automatically attached to a copy. A Zurich institution may add a meaningful institutional stage without a new city on the map.

Locality-level record counts: {'Zürich': 71, 'Rheinau': 253, 'Luzern': 23}. Records mentioning mapped institutions in more than one locality: 12.

Other institutions and all individual people remain unresolved in this bounded pilot. Authority IDs are matched exactly; the Luzern locality comes from the catalogue label, not an independently retrieved GND record. Source subfields are retained for scope and uncertainty review. No coordinates or timeline stations are generated.

## Reproduce

Run `python scripts/map_postincunabula_institutions.py` after the earlier collection and assessment steps. The live map is not modified.
