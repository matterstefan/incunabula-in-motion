# Zurich MARC feasibility probe — 22 October 2026

## Result

Public MARCXML retrieval is working for both Zurich Alma SRU and swisscollections SRU, without an API key. A bounded comparison of 21 bibliographic records supports a small prototype, but not an automatic conversion of every ownership statement into a dated map point. No website or map data has been changed.

Six incunabula were deliberately matched against the existing Zurich MEI snapshot using the institution, exact returned shelfmark and compatible title. Six sixteenth-century titles were selected for closer inspection. The full retrieval also includes related call-number hits and other results from the year 1531. This is a convenience sample, not a quantitative comparison of cataloguing practice across centuries.

## Access routes tested

- Zurich Alma SRU: `https://uzb.swisscovery.ch/view/sru/41SLSP_UZB` with `recordSchema=marcxml`.
- swisscollections SRU: `https://sru.swisscollections.ch/swisscollections` with `recordSchema=marc21-xml`.
- Both support SRU 1.2 `explain` and `searchRetrieve`.
- The Zurich institutional zone includes UB and ZB material. It is not equivalent to the ZB collection. In the sampled records, `Z06` identifies ZB Alte Drucke. Filtering by this code is appropriate for this initial sample, not necessarily for every ZB special collection.
- swisscollections `sc.possessingInstitution=Z06` and `sc.callnumber` located the known copies; returned 852/949 fields then supplied the local Alma bibliographic ID in `$9`.
- Alma retrieval by those exact MMS IDs returned 21 records. AVA includes the local bibliographic ID, holding ID, library, shelfmark and item count. These are **holding records, not item identifiers**.
- The Alma explain response advertises `alma.f561a`. A wildcard test combined with a date range returned a diagnostic (202319, wildcard unsupported in Community Zone), not zero matches. No conclusion about missing provenance can be drawn from that failed query.
- The swisscollections call-number query using `exact` nevertheless returned related signatures (e.g. `2.147`, `2.147,3`, `2.147: b`). Therefore query matches alone are not copy identification: inspect returned shelfmarks and publication statements.

Raw responses and exact request URLs are retained under `data/research/marc-pilot-20261022/`. The complete research sample is small and does not require another MEI harvest or any CERL access credential.

## Observations across the 21 compared title records

| Observation | Records |
| --- | ---: |
| Contains 361 | 0 |
| Contains 561 | 4 |
| Contains 563 | 5 |
| Contains former-owner access points (700/710/711 `$4=fmo`) | 14 |
| More than one ZB holding in the response | 2 |
| Only an `Online` shelfmark placeholder | 1 |

The 361, 561 and 563 fields and former-owner access points agree between the Alma and swisscollections responses in this sample. This is not evidence that the endpoints always expose every internal Alma field or full holding/item record.

## Focused examples

### Incunabula already present in MEI

| ZB shelfmark | Short title | Alma MMS ID | MEI ID | Finding |
| --- | --- | --- | --- | --- |
| Ink K 329,12 | De creatione Adae et formatione Evae | 990047941940205508 | 02129563 | No 561; former owner Kantonsbibliothek Zürich in 710, with GND identifier. |
| Ink K 342,7 | Summula mit Kommentar und Interlinearglosse | 990047733730205508 | 02129360 | 561 names Grossmünster library and a Kantonsbibliothek stamp; 710 supplies linked institutions. 949 gives a different ordering signature for the bound volume. |
| Ra 2 | Codex Iustinianus | 990045665310205508 | 02129912 | Kloster Rheinau as former owner in 710; no 561 in the response. |
| Rb 3,4 | Casus longi super Digesto novo | 990047317990205508 | 00570263 | Former owners Kantonsbibliothek Zürich and Kloster Rheinau in 710. 949 instructs ordering by Rb 3. |
| 4.276 | De nativitatibus | 990048649500205508 | 02129976 | No 561 or former-owner access point: the MARC response does not duplicate the MEI provenance detail. |
| 2.147 | Carmina de urinarum iudiciis | 990037626940205508 | 02129744 | 561 records annotations and a donation inscription dated MDCCLXIX; 700/710 link Heidegger and Stadtbibliothek Zürich. |

These are checked identity candidates, not permission to merge all statements automatically. Different imprint datings and different levels of detail remain source-specific.

### Sixteenth-century prints

| ZB shelfmark | Short title / year | Alma MMS ID | Finding |
| --- | --- | --- | --- |
| IV H 1 \| F | Biondo, De Roma triumphante, 1531 | 990070507980205508 | Conrad and Samuel Pellicanus are former owners in 700 with GND identifiers, although 561 is absent. Their biographical dates are not ownership dates. |
| Rm 56 \| G | Theophylactus, In quatuor Evangelia, 1531 | 990036481340205508 | A Rheinau ownership inscription is described in **563**, not 561; a corresponding former-owner 710 is present. |
| 18.280,14 | Paracelsus, Auslegung des Cometen, 1531 | 990053546370205508 | No 561 or former-owner entry in this response; ordering note refers to 18.280. |
| 3.161; III Q 351 | Bekandtnuß der vier Frey- und Reichstätt, 1531 | 990060026240205508 | One bibliographic record has two distinct ZB holdings/signatures. These must remain separate copy candidates. |
| 10.430,4 | Telesio, De coronarum generibus, 1531 | 990043572860205508 | 561 names Heinrich Bullinger and evidence on the fore-edge of the Sammelband; linked GND owner in 700. This is not grounds for transferring the evidence to every bound-with print without review. |
| 2.147: b | Pomponius Mela, Geographiae libri tres, 1512 | 990037763520205508 | 561 explicitly mentions a purchase note dated Vienna 1517 and a donation to Stadtbibliothek Zürich dated 1780. This is a promising first event-extraction example. |

The year-1531 query also returned a Bible record whose shelfmark is only `Online`. That must not become an additional physical copy or a journey endpoint.

## Proposed import mapping

| Information | MARC evidence | Import rule |
| --- | --- | --- |
| Edition / source record | 001, 035, 510; 245, 260/264, 008 | Preserve source system and IDs; keep each printing statement together. |
| Holding / candidate copy | Alma AVA `$0`, `$8`, `$b`, `$d`, `$f`; swisscollections 852/949 `$9`, `$b`, `$j` | Distinguish bibliographic, holding and item identity. A single holding is not universally a single item. |
| Narrative provenance | 561 `$a`, with `$3`, `$5`, `$8` where present | Retain original text and scope; extract candidate events only when justified. |
| Structured provenance | 361 `$a`, `$f`, `$k/$l`, `$o`, `$s/$y`, `$0/$1`, `$5`, `$z` | Schema-supported, but not yet tested against an actual ZB 361 record. Preserve ambiguity and public/private status. |
| Earlier owners | 700/710/711 `$4=fmo`, `$a`, `$0`; `$5` if supplied | Owner evidence, not automatically a place or a dated stay. 700 `$d` normally gives the person's dates, not the copy's dates. |
| Material evidence and supplementary notes | 563, potentially 500/541/562 and local fields | Review alongside the provenance fields; do not treat every binding note as an ownership event. |
| Bound-with / ordering relationships | 949 public notes, other links | Keep the bibliographic part, physical volume and ordering signature distinct. |

Institution-level `$5` does not by itself distinguish two copies held by that institution. A field without explicit copy scope must be reviewed when more than one holding is present. 361 `$y` may reference a holding rather than an individual item. Non-public 361 `$x`, or 361/561 fields flagged private, must not feed the public interface.

There is no dedicated geographic coordinate subfield in the 361 structure. A person or corporate-body authority identifier is not in itself proof that a copy stayed at a place associated with that entity. Geography must remain grounded in the ownership evidence or an explicitly reviewed institutional identification.

## Next bounded step

Build an **offline candidate adapter** for the twelve focused cases. Output source field occurrences, owner identifiers, candidate holdings and explicit date/place evidence. Keep unresolved identity, geography and chronology in separate review queues. Compare selected incunabula events with MEI without duplicating the same evidence. Do not yet merge these records into the public map.

Before scaling, clarify with ZB cataloguing staff whether relevant 561/361 data also resides in full holdings or item-level notes not exposed by these responses, and whether an approved sample export can include item IDs and links. Direct public SRU is adequate for this bounded probe; completeness for production is still unproven.

## Reproduce the comparison

```sh
python3 scripts/analyse_marc_pilot.py
```

This is offline and uses the saved responses plus the existing Zurich MEI snapshot. It writes `comparison.json`; it does not change `data/map/`. Request URLs are saved next to their XML responses for later deliberate re-retrieval.

## Documentation consulted

- [ZB Data Map: Alma SRU](https://data.zb.uzh.ch/map/books/data-map-der-zentralbibliothek-zurich/page/alma-sru)
- [swisscollections SRU specification](https://ub-basel.atlassian.net/wiki/spaces/swisscollections/pages/1974370315/SRU-Schnittstelle)
- [Alma publishing for swisscollections](https://ub-basel.atlassian.net/wiki/spaces/swisscollections/pages/3269623815/Alma+Publishing+f+r+swisscollections): publishing includes physical holdings and item enrichment; this is not a guarantee of every original internal field.
- [Ex Libris: SRU](https://developers.exlibrisgroup.com/alma/integrations/sru/)
- [Library of Congress: 561](https://www.loc.gov/marc/bibliographic/bd561.html)
- [Library of Congress: 361](https://www.loc.gov/marc/bibliographic/bd361.html)
