import unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('owners',ROOT/'scripts/prepare_owner_decisions.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d,cls.rows,cls.s=m.build()
 def test_identity_and_counts(self):
  self.assertEqual({d['gnd_id'] for d in self.d},set(m.IDS))
  for d in self.d:
   rows=[r for r in self.rows if r['gnd_id']==d['gnd_id']]
   self.assertEqual(len(rows),d['references'])
   self.assertEqual(sum(not r['existing_place_candidates'] for r in rows),d['without_any_prepared_place'])
   for r in rows:
    self.assertTrue(r['owner_fields'])
    for f in r['owner_fields']:
     self.assertIn(['0','(DE-588)'+d['gnd_id']],f['subfields'])
     self.assertIn([r['institution_code'],r['shelfmark']],f['targets'])
 def test_union_not_sum(self):
  keys={m.key(r) for r in self.rows}
  self.assertEqual(len(keys),self.s['unique_references_in_four_groups'])
  self.assertLess(len(keys),len(self.rows))
 def test_use_not_forced_ownership(self):
  rows=[r for r in self.rows if r['record_id']=='991012344199705501' and r['gnd_id']=='118694413']
  self.assertEqual(len(rows),1);self.assertTrue(rows[0]['explicit_gessner_use_at_grossmuenster'])
  self.assertTrue(all(r['decision_status']=='pending_discussion' for r in self.rows))
 def test_repeatable(self):self.assertEqual((self.d,self.rows,self.s),m.build())
if __name__=='__main__':unittest.main()
