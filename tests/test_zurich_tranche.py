import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('tranche', Path(__file__).resolve().parents[1] / 'scripts/collect_zurich_tranche.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def page(total, ids, extra=''):
    records = ''.join(f'<record><recordData><m:record><m:leader>00000nam a2200000   4500</m:leader><m:controlfield tag="001">{i}</m:controlfield>{extra}</m:record></recordData></record>' for i in ids)
    return f'<searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/" xmlns:m="http://www.loc.gov/MARC21/slim"><numberOfRecords>{total}</numberOfRecords><records>{records}</records></searchRetrieveResponse>'.encode()

class TestTranche(unittest.TestCase):
    def test_scope(self):
        q = m.query_for(1526, 1550)
        for i in range(1, 7):
            self.assertIn(f'Z{i:02}', q)
        self.assertIn('dc.date <= 1550', q)

    def test_resume_paginated_short_pages(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            responses = iter([page(3, ['a', 'b']), RuntimeError('interruption')])
            def fetch(url):
                value = next(responses)
                if isinstance(value, Exception): raise value
                return value
            with self.assertRaises(RuntimeError): m.harvest(out, 'test', fetch)
            calls = []
            def resume(url):
                calls.append(url)
                return page(3, ['c'])
            records, pages = m.harvest(out, 'test', resume)
            self.assertEqual(len(records), 3)
            self.assertEqual(len(calls), 1)
            self.assertIn('startRecord=3', calls[0])

    def test_reject_duplicate_or_changed_total(self):
        for second in [page(2, ['a']), page(3, ['b'])]:
            with tempfile.TemporaryDirectory() as folder:
                responses = iter([page(2, ['a']), second])
                with self.assertRaises(ValueError):
                    m.harvest(Path(folder), 'test', lambda _: next(responses))

    def test_empty_and_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            records, _ = m.harvest(Path(folder), 'test', lambda _: page(0, []))
            self.assertEqual(records, [])
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                m.harvest(Path(folder), 'test', lambda _: page(50001, ['a']))

    def test_scope_and_private_fields_not_conflated(self):
        extra = '''<m:datafield tag="852"><m:subfield code="b">Z03</m:subfield><m:subfield code="j">A 1</m:subfield></m:datafield>
        <m:datafield tag="852"><m:subfield code="b">Z06</m:subfield><m:subfield code="j">B 1</m:subfield></m:datafield>
        <m:datafield tag="561" ind1="0"><m:subfield code="a">Private</m:subfield></m:datafield>
        <m:datafield tag="700"><m:subfield code="a">Owner</m:subfield><m:subfield code="4">fmo</m:subfield><m:subfield code="0">GND</m:subfield></m:datafield>'''
        _, records = m.parse_page(page(1, ['a'], extra))
        counts, rows = m.profile(records, 1526, 1550)
        self.assertEqual(counts['catalogue_references'], 2)
        self.assertEqual(counts['records_with_owner_authority'], 1)
        self.assertEqual(counts['records_with_561'], 0)
        self.assertFalse(any(f['tag'] == '561' for f in rows[0]['fields']))
        self.assertNotIn('stations', rows[0])

if __name__ == '__main__': unittest.main()
