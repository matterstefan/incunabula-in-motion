# Provenance field inventory: all-ZB working corpus

Offline analysis, 23 October 2026. The denominator is 4,396 exported records containing 5,149 retained catalogue copy references. The 45 reproduction-review references remain included. Counts below are records, not physical copies.

## Field coverage

| Field | Records containing field | Records with core indicator |
|---|---:|---:|
| 561 | 526 | 526 |
| 361 | 0 | 0 |
| 700 | 3062 | 907 |
| 710 | 1657 | 365 |
| 563 | 449 | 0 |
| 590 | 1688 | 0 |
| 500 | 3097 | 0 |
| 596 | 1 | 0 |
| 949 | 4153 | 0 |
| 541 | 0 | 0 |
| 562 | 0 | 0 |

1,212 records contain a core indicator (561/361 or a former-owner role). These categories overlap. Another 32 records contain stronger lexical candidates in note fields, without a core indicator. The latter are candidates, not 32 confirmed additional provenance histories. Generic stamp mentions alone are excluded from this stronger candidate count. No absence of provenance can be inferred from a failure to match this limited vocabulary.

The inventory counts the exported fields; it does not determine their original storage level inside Alma. Links, titles and subject terms must not be interpreted as ownership evidence. URLs were removed from lexical scanning to avoid matching the software domain exlibrisgroup.com. Repeated-note grouping is exact-text grouping, not owner identity resolution.

## Examples for joint review

### 1. Explicit copy scope

Record: 991019857919705501. Title: C. Plinii Secvndi Novocomensis epistolaru[m] libri Decem in quibus multæ habentur epistolæ non ante impressæ ... Item fragmentatæ epistolæ, integræ factæ. In medio etiam epistolæ libri octaui de Clitumno fonte non solum uertici calx additus, et calci uertex, sed decem quoq[ue] epistolæ interpositæ .... Retained shelfmarks: 4.305.

```text
561 $a Gelangte 1839 als Donation von Johann Kaspar von Orelli in den Besitz der Stadtbibliothek Zürich, mit dessen hs. Schenkungsvermerk auf dem vord. Vorsatzblatt.
561 $5 Exemplar ZB Zürich (4.305)
```

The scope names 4.305; the note names a donor, receiving library and year. These relationships are stated in the catalogue.

### 2. Ownership in a general note

Record: 991001165399705501. Title: M. Actii Plauti Asinii, comici claris, simi comoediae quinque. Retained shelfmarks: 4.221.

```text
500 $a Handschriftlicher Besitzvermerk: Capar Hagenbuchii, datiert 1753
```

A dated ownership inscription outside 561. Preserve the source spelling Capar Hagenbuchii; no place is supplied.

### 3. Uncertain owner

Record: 991010863959705501. Title: <<Eyn>> Sendbrieff widder den newen yrrthumb bey dem Sacrament des leybs und blutts unseres Herrn Jhesu Christi. Retained shelfmarks: III O 173: b,7.

```text
500 $a Vorbesitzer Zwingli, Huldrych: unsicher
```

The catalogue explicitly says unsicher. Do not promote this to certain ownership.

### 4. Several owners in a local note

Record: 991000419389705501. Title: Vita Christi (franz.). Retained shelfmarks: MLW 108.

```text
590 $a Holzschnitte und Holzschnittinitialen koloriert; rubriziert (teils mit hs. roten Überschriften); hs. Register auf 4 Nachsatzbl
590 $a Hs. Besitzvermerk der Kartäuserinnen Gosnay bei Béthune und einer "dame Izabeau Dassignies" auf Bl. 2r; nicht indentifiziertes Exlibris im vorderen Spiegel
590 $a Dunkler Ledereinband mit Blindprägungen (20 Jh.), Marmorpapier (Spiegel, Vor- u. Nachsatz), Goldschnitt
```

Gosnay near Béthune is stated; another owner and an unidentified exlibris occur in the same note. No chronology should be invented.

### 5. Donation with ambiguous copy scope

Record: 991001105039705501. Title: Epythoma pariter et collectorium circa quattuor sententiarum libros. Retained shelfmarks: IV S 61-62 | G; Rm 106: c | G.

```text
590 $a Schweinsledereinband der Zeit. Zierinitialen. Von Konrad Pellikan um 1540 der Bibliothek des Grossmünsterstifts geschenkt. Mit hs. Annotationen
```

Two retained signatures occur in the record. The note names Pellikan, the Grossmünster library and circa 1540, but does not itself identify which signature it concerns.

### 6. Note tied to a shelfmark

Record: 991002418219705501. Title: Parochiale curatorum. Retained shelfmarks: Res 915; RRr 125.

```text
949 $c RAM
949 $z Aus dem Vorbesitz des Klosters Rheinau. Mit wenigen handschr. Annotationen
949 $p 12
949 $j RRr 125
949 $b Z06
949 $9 (41SLSP_UZB)990056262180205508
```

949$z names Rheinau and 949$j identifies RRr 125, distinguishing it from Res 915. This is stronger copy evidence than record-level co-occurrence.

### 7. Ownership in another local field

Record: 991022084669705501. Title: <<Ein>> nutzliche vnderwisung eines Christenliche[n] fürsten wol zů regieren. Retained shelfmarks: Zwingli 243.

```text
596 $a Auf dem Titelblatt Besitz- und Preisvermerk: "Frow Agnes Masei [Meiss?], 10 Btz.". Auf dem vorderen Vorsatzblatt Besitzvermerk: "Ulrich Meiss"
```

Two inscriptions, including an uncertain reading Meiss?, are preserved. A price is not a date.

### 8. Negative control: binding decoration

Record: 991000877379705501. Title: Codicis Justiniani amplissimu[m] Argume[n]tum. Retained shelfmarks: H 42 | F.

```text
563 $a Schweinsledereinband der Zeit mit Rollenstempeln und Stempeln verziert, mit zwei Metallschliessen
```

Rollenstempel and decorative stamps do not by themselves identify a former owner.

## Next interpretation step

Review these eight examples before extending attribution rules. In particular, use an exact institution/shelfmark association within 949 for its own note, without propagating scope to unrelated fields. Keep uncertainty, named people, named institutions, dates and explicit places separate. A date or place in a note is not automatically the date/place of an ownership event. No map import or authority enrichment was performed.

## Reproducibility

Run `python3 scripts/inventory_postincunabula_fields.py /path/to/2026-10-23-17h15.zip` after the baseline and reproduction scripts. Outputs: field-inventory.json, field-candidates.json and repeated-note-candidates.json. The candidate file retains original subfields and record/shelfmark context. Restricted 561/361 fields (indicator 1 = 0) are not exported as candidates.
