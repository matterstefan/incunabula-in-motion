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
            responses = iter([page(3, ['a', 'b']), TimeoutError('interruption')])
            def fetch(url):
                value = next(responses)
                if isinstance(value, Exception):
                    raise value
                return value
            records, _, status = m.harvest(out, 'test', fetch)
            self.assertEqual(len(records), 2)
            self.assertFalse(status['complete'])
            self.assertEqual(status['request_error']['start_record'], 3)
            calls = []
            def resume(url):
                calls.append(url)
                return page(3, ['c'])
            records, pages, status = m.harvest(out, 'test', resume)
            self.assertEqual(len(records), 3)
            self.assertTrue(status['complete'])
            self.assertTrue(pages[0]['loaded_from_cache'])
            self.assertEqual(len(calls), 1)
            self.assertIn('startRecord=3', calls[0])

    def run_pages(self, responses):
        with tempfile.TemporaryDirectory() as folder:
            responses = iter(responses)
            return m.harvest(Path(folder), 'test', lambda _: next(responses))

    def test_duplicates_are_retained_once_and_shortfall_reported(self):
        records, _, status = self.run_pages([page(4, ['a', 'b']), page(4, ['b', 'c'])])
        self.assertEqual([m.rid(r) for r in records], ['a', 'b', 'c'])
        self.assertTrue(status['page_traversal_finished'])
        self.assertFalse(status['complete'])
        self.assertEqual(status['rows_returned'], 4)
        self.assertEqual(status['duplicate_occurrences'], 1)
        self.assertEqual(status['shortfall_against_reported_total'], 1)

    def test_entire_repeated_page_still_advances(self):
        records, _, status = self.run_pages([page(4, ['a', 'b']), page(4, ['a', 'b'])])
        self.assertEqual(len(records), 2)
        self.assertTrue(status['page_traversal_finished'])
        self.assertEqual(status['duplicate_occurrences'], 2)
        self.assertIsNone(status['request_error'])

    def test_changed_total_is_unverified(self):
        _, _, status = self.run_pages([page(2, ['a']), page(3, ['b'])])
        self.assertFalse(status['complete'])
        self.assertFalse(status['reported_total_stable'])
        self.assertIsNone(status['shortfall_against_reported_total'])

    def test_empty_result_and_invalid_response(self):
        records, _, status = self.run_pages([page(0, [])])
        self.assertEqual(records, [])
        self.assertTrue(status['complete'])
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            _, _, status = m.harvest(out, 'test', lambda _: b'<error/>')
            self.assertFalse(status['complete'])
            self.assertIn('numberOfRecords', status['request_error']['message'])
            self.assertEqual((out / 'diagnostics-v4/0000001.xml').read_bytes(), b'<error/>')
            self.assertFalse((out / 'pages/0000001.xml').exists())

    def test_conflicting_repeat_keeps_first_version(self):
        changed = '<m:datafield tag="245"><m:subfield code="a">Changed</m:subfield></m:datafield>'
        records, _, status = self.run_pages([page(2, ['a']), page(2, ['a'], changed)])
        self.assertEqual(len(records), 1)
        self.assertIsNone(records[0].find("m:datafield[@tag='245']", m.NS))
        self.assertEqual(status['conflicting_repeat_occurrences'], 1)
        self.assertFalse(status['complete'])

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
