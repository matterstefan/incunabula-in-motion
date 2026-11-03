#!/usr/bin/env python3
"""Offline MARC record inventory; no density scores or inferred events."""
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

NS = '{http://www.loc.gov/MARC21/slim}'
NOTE_TAGS = ('361', '541', '561', '562', '563', '565', '590', '591', '595', '596')
CONTEXT_TAGS = ('300', '500', '852', '949')
PATTERNS = {
    'ownership_text_hint': r'vorbesitz|besitzvermerk|besitzeintrag|besitzeinträge|ex.?libris|aus der sammlung|provenienz|possessor',
    'binding_text_hint': r'einband|einbände|lederband|pappband|pergamentband|schweinsleder|buchbind|blindpräg|blindpress|goldpräg|werkstatt',
    'waste_text_hint': r'makulatur',
    'use_text_hint': r'annotat|marginal|randnot|unterstreich|rubriz|kolorier|handschriftliche.*notiz',
    'gift_text_hint': r'schenkung|schenkungsvermerk|widmung|dedikation|donum|donat',
}
LABELS = {
    'structured_owner': 'Vorbesitzer in 700/710/711 mit entsprechender Rolle',
    'owner_authority': 'Solcher Vorbesitzer mit Normdatenkennung ($0/$1)',
    'owner_gnd': 'Solcher Vorbesitzer mit erkennbarer GND-Kennung',
    'owner_name_without_authority': 'Mindestens ein Vorbesitzername ohne $0/$1',
    'any_selected_note': 'Text in mindestens einem ausgewählten Notizfeld',
    'owner_or_selected_note': 'Vorbesitzerrolle oder ausgewähltes Notizfeld',
    'neither_owner_nor_selected_note': 'Weder Vorbesitzerrolle noch ausgewähltes Notizfeld',
    'ownership_text_hint': 'Suchwortsignal zu Besitz in Notizen (ungeprüft)',
    'binding_text_hint': 'Suchwortsignal zu Einband in Notizen (ungeprüft)',
    'waste_text_hint': 'Suchwortsignal Makulatur in Notizen (ungeprüft)',
    'use_text_hint': 'Suchwortsignal zu Benutzung/Ausstattung (ungeprüft)',
    'gift_text_hint': 'Suchwortsignal zu Schenkung/Widmung (ungeprüft)',
}

def sf(f, codes):
    return [s.text or '' for s in f if s.get('code') in codes]

def meaningful(f):
    # Linkage, authority, institution and technical subfields alone are not note text.
    return ' '.join(s.text.strip() for s in f if s.get('code', '').isalpha()
                    and s.text and s.text.strip())

def field_data(f):
    return {'tag': f.get('tag'), 'ind1': f.get('ind1', ' '), 'ind2': f.get('ind2', ' '),
            'subfields': [[s.get('code'), s.text or ''] for s in f]}

def owner(f):
    return (f.get('tag') in ('700', '710', '711') and
            ('fmo' in [v.strip().lower() for v in sf(f, '4')] or
             any(re.search(r'vorbesitzer|frühere[rns]? eigentümer|former owner|ancien possesseur', v, re.I)
                 for v in sf(f, 'e'))))

def analyze(r):
    rid = r.findtext(NS + 'controlfield[@tag="001"]')
    if not rid:
        raise ValueError('Record without MARC 001')
    allfields = r.findall(NS + 'datafield')
    private = [f for f in allfields if f.get('tag') in ('361', '541', '561') and f.get('ind1') == '0']
    fields = [f for f in allfields if f not in private]
    owners = [f for f in fields if owner(f) and any(v.strip() for v in sf(f, 'a'))]
    notes = [f for f in fields if f.get('tag') in NOTE_TAGS and meaningful(f)]
    counts = {t: sum(f.get('tag') == t for f in notes) for t in NOTE_TAGS}
    flags = {'structured_owner': bool(owners),
             'owner_authority': any(any(v.strip() for v in sf(f, '01')) for f in owners),
             'owner_gnd': any(any(re.search(r'DE-588|d-nb\.info/gnd/', v, re.I) for v in sf(f, '01')) for f in owners),
             'owner_name_without_authority': any(not any(v.strip() for v in sf(f, '01')) for f in owners),
             'any_selected_note': bool(notes),
             'owner_or_selected_note': bool(owners or notes),
             'neither_owner_nor_selected_note': not (owners or notes)}
    flags.update({'field_' + t: bool(counts[t]) for t in NOTE_TAGS})
    hints = {}
    # General 500 notes are searched too, but are not presumed copy-specific.
    search_fields = notes + [f for f in fields if f.get('tag') == '500' and meaningful(f)]
    for key, pattern in PATTERNS.items():
        hits = [field_data(f) for f in search_fields if re.search(pattern, meaningful(f), re.I)]
        hints[key] = hits
        flags[key] = bool(hits)
    date = r.findtext(NS + 'controlfield[@tag="008"]', default='')
    return {'record_id': rid, 'catalogue_url': 'https://swisscollections.ch/Record/' + rid,
            'title': ' '.join(v for f in fields if f.get('tag') == '245' for v in sf(f, 'ab')),
            'flags': flags, 'note_field_occurrences': counts,
            'note_characters': sum(len(meaningful(f)) for f in notes),
            'owners': [field_data(f) for f in owners], 'notes': [field_data(f) for f in notes],
            'keyword_evidence': hints,
            'context': [field_data(f) for f in fields if f.get('tag') in CONTEXT_TAGS],
            'explicit_scope_subfield5': sorted({v for f in notes + owners for v in sf(f, '5') if v.strip()}),
            'private_note_fields_omitted': len(private),
            'date_008': date[6:15], 'reproduction_date_code': date[6:7] == 'r'}

def inventory(source, output):
    source, output = Path(source), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    raw_records = {}; duplicate_count = 0
    with zipfile.ZipFile(source) as z:
        pages = sorted(n for n in z.namelist() if 'pages' in Path(n).parts and n.endswith('.xml')
                       and '__MACOSX' not in Path(n).parts and not Path(n).name.startswith('._'))
        if not pages:
            raise ValueError('No raw SRU pages found in input ZIP')
        for name in pages:
            for r in ET.fromstring(z.read(name)).iter(NS + 'record'):
                rid = r.findtext(NS + 'controlfield[@tag="001"]')
                if not rid:
                    raise ValueError('Record without MARC 001')
                signature = [(e.tag, sorted(e.attrib.items()), (e.text or '').strip()) for e in r.iter()]
                if rid in raw_records:
                    duplicate_count += 1
                    if raw_records[rid][0] != signature:
                        raise ValueError('Conflicting versions of record ' + rid)
                else:
                    raw_records[rid] = (signature, r)
        metadata = {}
        for basename in ('request-v4.json', 'retrieval-status.json'):
            matches = [n for n in z.namelist() if Path(n).name == basename and '__MACOSX' not in Path(n).parts]
            if len(matches) == 1:
                metadata[basename] = json.loads(z.read(matches[0]))
    rows = [analyze(raw_records[k][1]) for k in sorted(raw_records)]
    n = len(rows)
    if not n:
        raise ValueError('No records')
    counts = Counter(k for row in rows for k, value in row['flags'].items() if value)
    labels = {**LABELS, **{'field_' + t: 'Nichtleeres Textfeld MARC ' + t for t in NOTE_TAGS}}
    metrics = [{'key': k, 'label': label, 'records': counts[k], 'denominator': n,
                'percent': round(100 * counts[k] / n, 2)} for k, label in labels.items()]
    summary = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
               'records': n, 'raw_pages': len(pages), 'duplicate_rows_removed': duplicate_count,
               'metrics': metrics, 'source_metadata': metadata,
               'records_with_private_note_omissions': sum(bool(r['private_note_fields_omitted']) for r in rows),
               'records_with_explicit_note_or_owner_scope': sum(bool(r['explicit_scope_subfield5']) for r in rows),
               'records_with_reproduction_date_code': sum(r['reproduction_date_code'] for r in rows)}
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    with (output / 'records.jsonl').open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    # Contrastive examples, intentionally not a representative sample or classification.
    sample = []
    for label, group in [
        ('Ohne ausgewählte Notiz und ohne Vorbesitzerrolle', [r for r in rows if r['flags']['neither_owner_nor_selected_note']]),
        ('Kurze Notizen ohne Vorbesitzerrolle', sorted([r for r in rows if r['notes'] and not r['owners']], key=lambda r: r['note_characters'])),
        ('Lange Notizen ohne Vorbesitzerrolle', sorted([r for r in rows if r['notes'] and not r['owners']], key=lambda r: -r['note_characters'])),
        ('Notizen und Vorbesitzerrolle', sorted([r for r in rows if r['notes'] and r['owners']], key=lambda r: -r['note_characters']))]:
        sample.extend({'selection_reason': label, **r} for r in group[:3])
    (output / 'review-sample.json').write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding='utf-8')
    table = ''.join('<tr><td>' + html.escape(m['label']) + f"</td><td>{m['records']:,}</td><td>{m['percent']:.1f}%</td></tr>" for m in metrics)
    detail = ''.join('<details><summary>' + html.escape(r['record_id'] + ' — ' + r['title']) + '</summary><p>'
                     + html.escape(r['selection_reason']) + '</p><pre>'
                     + html.escape(json.dumps(r, ensure_ascii=False, indent=2)) + '</pre></details>' for r in sample)
    report = f'''<!doctype html><html lang="de"><meta charset="utf-8"><title>Kataloginventar</title>
<style>body{{font:16px/1.5 system-ui;max-width:1050px;margin:40px auto;padding:0 24px;color:#183044}}table{{border-collapse:collapse;width:100%}}td,th{{padding:9px;border-bottom:1px solid #ccd6df;text-align:left}}td:nth-child(n+2){{text-align:right}}th{{background:#e5eff4}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}summary{{cursor:pointer;padding:12px 0}}</style>
<h1>Kataloginventar: Aufnahmeprofil</h1><p>{n:,} unterschiedliche Aufnahmen. Eine Aufnahme zählt pro Merkmal höchstens einmal. Keine Band- oder Ereigniszählung.</p>
<p>Grundlage: {html.escape(source.name)}. Die technische Abrufbilanz bleibt in summary.json erhalten. Keine Materialausschlüsse oder zeitlichen Nachfilterungen. Für die Tranche 1551–1600 vom 3. November 2026 hat die Projektleitung den Bestand als ausreichend vollständig für die Analyse akzeptiert.</p>
<h2>Abdeckung auf Aufnahmeebene</h2><table><tr><th>Merkmal</th><th>Aufnahmen</th><th>Anteil</th></tr>{table}</table>
<h2>Leseregeln</h2><p>Feldpräsenz ist noch keine Dichteklasse. Notizfelder können auch administrative Angaben enthalten. Suchwortsignale sind ungeprüfte Kandidaten, keine gesicherten historischen Aussagen; Widmungen können etwa gedruckt statt exemplarspezifisch sein. Nichttreffer bedeuten nicht, dass der ganze Katalogtext informationslos ist. Allgemeine 500-Notizen werden bei Suchworten berücksichtigt, aber nicht pauschal als Exemplarnotizen gezählt.</p>
<p>Notizen und normierte Namen können dieselbe Spur erschliessen. Die Merkmale dürfen daher nicht zu Ereigniszahlen addiert werden. Aussagen beziehen sich auf die gesamte Aufnahme; $5-Zuordnungen bleiben erhalten und sind vor Aussagen zum konkreten ZB-Exemplar zu lesen. 300, 852 und 949 bleiben Kontext, ohne Mehrbändigkeit als Problemfall zu markieren. Private 361/541/561-Felder (Indikator 0) werden nicht ausgegeben; ihre Auslassung ist separat gezählt.</p>
<p>records.jsonl enthält genau eine Zeile pro Aufnahme mit Flags und Originalfeldern. summary.json enthält Nenner, Abfrage und Prüfstatus. Die folgenden zwölf Beispiele sind eine gezielte Auswahl zur Kalibrierung, keine repräsentative Stichprobe.</p>
<h2>Beispiele für die gemeinsame Durchsicht</h2>{detail}</html>'''
    (output / 'Uebersicht.html').write_text(report, encoding='utf-8')
    record_table = []
    for row in rows:
        tags = ', '.join(t for t, count in row['note_field_occurrences'].items() if count)
        cells = [row['title'], 'ja' if row['flags']['structured_owner'] else 'nein',
                 'ja' if row['flags']['owner_authority'] else 'nein', tags, str(row['note_characters'])]
        record_table.append('<tr><td><a href="' + row['catalogue_url'] + '">' + html.escape(row['record_id'])
                            + '</a></td>' + ''.join('<td>' + html.escape(v) + '</td>' for v in cells) + '</tr>')
    (output / 'Aufnahmen.html').write_text('''<!doctype html><html lang="de"><meta charset="utf-8"><title>Aufnahmeninventar</title>
<style>body{font:14px/1.4 system-ui;margin:24px}table{border-collapse:collapse;width:100%}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}th{position:sticky;top:0;background:#e5eff4}td:first-child{white-space:nowrap}tr:nth-child(even){background:#f6f8fa}</style>
<h1>Eine Zeile pro Katalogaufnahme</h1><p>Mit der Suchfunktion des Browsers nach Titel oder MARC-ID suchen. Notizzeichen und Feldpräsenz sind keine Dichtebewertung. Normdaten: Vorbesitzer mit $0/$1. Originalstellen in records.jsonl; Regeln und Übersicht in Uebersicht.html.</p>
<table><thead><tr><th>MARC-ID / Kataloglink</th><th>Titel</th><th>Vorbesitzerrolle</th><th>Normdaten</th><th>Notizfelder</th><th>Notizzeichen</th></tr></thead><tbody>'''
        + ''.join(record_table) + '</tbody></table></html>', encoding='utf-8')
    print(json.dumps({'records': n, 'metrics': metrics}, ensure_ascii=False, indent=2))
    return summary

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    inventory(args.source, args.output)
