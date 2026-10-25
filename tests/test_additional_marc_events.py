import unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('events',ROOT/'scripts/prepare_additional_marc_events.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class EventTests(unittest.TestCase):
 def setUp(self):self.rules=m.read(ROOT/'data/authority/postincunabula-additional-event-rules.json')['rules']
 def field(self,text,assignment='plausible',tag='561'):
  return {'assignment':assignment,'tag':tag,'subfields':[['a',text]]}
 def test_date_attached_to_event(self):
  out=m.extract(self.field('Kaufvermerk von Adrian Wirth, dat. Wien 1517, Schenkungsvermerk Caspar Orellis an Zürich, dat. 1780'),self.rules)
  self.assertEqual(len(out),1);self.assertEqual(out[0]['year'],1517);self.assertEqual(out[0]['place'],'Vienna')
 def test_unrelated_year_is_not_institution_event(self):
  self.assertEqual(m.extract(self.field('Emptus 1536; alte Signatur des Jesuitenkolleg Luzern'),self.rules),[])
  self.assertEqual(m.extract(self.field('Aus dem Vorbesitz des Klosters Rheinau. Weiterer Vorbesitzer Blecker (1609)'),self.rules),[])
 def test_unresolved_assignment_excluded(self):
  self.assertEqual(m.extract(self.field('Verbalexlibris des Klosters Rheinau (1611)',assignment='open'),self.rules),[])
 def test_person_lifespan_excluded(self):
  self.assertEqual(m.extract(self.field('Adrian Wirth 1490-1540',tag='700'),self.rules),[])
 def test_data_integrity(self):
  events,summary=m.build();self.assertTrue(events)
  self.assertEqual(len(events),len({(m.key(e),e['rule_id'],e['year']) for e in events}))
  for e in events:
   self.assertIn(e['matched_text'],m.text(e['evidence']))
   self.assertEqual(e['status'],'prepared_not_published')
   self.assertEqual(e['copy_assignment'],e['evidence']['assignment'])
   self.assertIn([e['institution_code'],e['shelfmark']],e['evidence']['targets'])
   self.assertTrue(e['coordinates']['source_url'].startswith('https://'))
  self.assertEqual(summary['new_references']+summary['references_already_in_first_pilot'],summary['distinct_references'])
  self.assertEqual(m.build(),m.build())
if __name__=='__main__':unittest.main()
