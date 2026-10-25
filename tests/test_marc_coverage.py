import unittest,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'scripts/summarise_marc_provenance_coverage.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CoverageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows,cls.groups,cls.s=m.build()
 def test_partition(self):
  s=self.s
  self.assertEqual(sum(s['assignment_categories_exclusive'].values()),s['working_references'])
  self.assertEqual(s['linked_core_indicator']+s['linked_lexical_only'],s['linked_any_candidate'])
  self.assertEqual(s['linked_any_candidate'],s['assignment_categories_exclusive']['explicit']+s['assignment_categories_exclusive']['plausible'])
 def test_place_and_date_sets(self):
  s=self.s
  self.assertEqual(s['strictly_undated_place_references']+s['references_with_any_recognised_dated_candidate'],s['all_prepared_places_union'])
  self.assertEqual(s['linked_references_without_prepared_places']+s['all_prepared_places_union']-s['prepared_place_without_linked_candidate'],s['linked_any_candidate'])
  self.assertLess(s['pilot_and_additional_union'],s['pilot_references']+s['additional_event_references'])
 def test_unique_reference_unit(self):
  self.assertEqual(len(self.rows),len({m.key(r) for r in self.rows}))
  self.assertTrue(all(r['record_id'] and r['institution_code'] for r in self.rows))
  self.assertEqual(sum(not r['shelfmark'] for r in self.rows),self.s['references_with_empty_852_shelfmark'])
 def test_group_deduplication(self):
  keys={m.key(r) for r in self.rows}
  for g in self.groups:
   groupkeys={tuple(k) for k in g['reference_keys']}
   self.assertEqual(g['references'],len(groupkeys));self.assertTrue(groupkeys<=keys)
   self.assertEqual(g['references_without_any_prepared_place']+g['references_with_some_prepared_place'],g['references'])
 def test_reproducibility_and_prior_totals(self):
  self.assertEqual((self.rows,self.groups,self.s),m.build())
  old=m.read(m.DATA/'collection-place-summary.json')
  self.assertEqual(self.s['prior_place_candidates_union'],old['combined_distinct_references'])
if __name__=='__main__':unittest.main()
