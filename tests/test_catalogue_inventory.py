import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).resolve().parents[1] / 'scripts/inventory_catalogue_records.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def record(extra=''):
    return ET.fromstring('<record xmlns="http://www.loc.gov/MARC21/slim"><controlfield tag="001">991000000000000001</controlfield>' + extra + '</record>')

class InventoryTests(unittest.TestCase):
    def test_multivolume_and_repeated_evidence_count_once(self):
        r = m.analyze(record('''<datafield tag="590"><subfield code="a">Exlibris</subfield></datafield>
        <datafield tag="590"><subfield code="a">Exlibris</subfield></datafield>
        <datafield tag="700"><subfield code="a">Owner</subfield><subfield code="4">fmo</subfield><subfield code="0">(DE-588)123</subfield></datafield>
        <datafield tag="852"><subfield code="j">Band 1</subfield></datafield>
        <datafield tag="852"><subfield code="j">Band 2</subfield></datafield>'''))
        self.assertTrue(r['flags']['structured_owner'])
        self.assertTrue(r['flags']['owner_gnd'])
        self.assertEqual(r['note_field_occurrences']['590'], 2)
        self.assertIs(r['flags']['ownership_text_hint'], True)
        self.assertEqual(len(r['context']), 2)

    def test_private_and_linkage_only_not_note_text(self):
        r = m.analyze(record('''<datafield tag="561" ind1="0"><subfield code="a">Secret owner</subfield></datafield>
        <datafield tag="590"><subfield code="5">ZBZ</subfield><subfield code="8">1</subfield></datafield>'''))
        self.assertFalse(r['flags']['any_selected_note'])
        self.assertEqual(r['private_note_fields_omitted'], 1)
        self.assertEqual(r['notes'], [])

    def test_general_notes_and_other_roles_not_conflated(self):
        r = m.analyze(record('''<datafield tag="500"><subfield code="a">Gedruckte Widmung</subfield></datafield>
        <datafield tag="700"><subfield code="a">Author</subfield><subfield code="4">aut</subfield></datafield>'''))
        self.assertFalse(r['flags']['structured_owner'])
        self.assertFalse(r['flags']['any_selected_note'])
        self.assertTrue(r['flags']['gift_text_hint'])
        self.assertEqual(r['keyword_evidence']['gift_text_hint'][0]['tag'], '500')

    def test_conflicting_duplicates_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            with zipfile.ZipFile(p/'input.zip', 'w') as z:
                z.writestr('pages/1.xml', ET.tostring(record()))
                z.writestr('pages/2.xml', ET.tostring(record('<datafield tag="590"><subfield code="a">New</subfield></datafield>')))
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                m.inventory(p/'input.zip', p/'out')

if __name__ == '__main__':
    unittest.main()
