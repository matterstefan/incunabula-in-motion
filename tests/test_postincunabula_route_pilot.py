"""Offline tests for semantic selection boundaries and source preservation."""
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pilot',ROOT/'scripts/prepare_postincunabula_route_pilot.py')
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

def field(text,rid='test',assignment='plausible',tag='561'):
    return {'record_id':rid,'tag':tag,'assignment':assignment,'subfields':[['a',text]],'targets':[['Z06','Test']]}

class PilotTests(unittest.TestCase):
    def test_donation_not_prior_purchase(self):
        e=p.dated_event(field('Im vorderen Spiegel Kaufvermerk von Adrian Wirth, dat. Wien 1517, sowie Schenkungsvermerk Caspar Orellis an die Stadtbibliothek Zürich, dat. 1780.'))
        self.assertEqual(e['year'],1780)
        self.assertEqual(e['owner_or_recipient'],'Stadtbibliothek Zürich')
    def test_birth_and_later_library_stamp_not_events(self):
        self.assertIsNone(p.dated_event(field('Orelli, Johann Caspar, 1787-1849',tag='700')))
        self.assertIsNone(p.dated_event(field('Besitzernotiz von 1649 im vorderen Spiegel; Supralibros der Stadtbibliothek Zürich')))
        self.assertIsNone(p.dated_event(field('Bibliotheca aedium pastoralium ab anno 1651; Supralibros der Stadtbibliothek Zürich')))
    def test_no_open_copy_assignment(self):
        self.assertIsNone(p.dated_event(field('Gelangte 1832 als Donation in den Besitz der Stadtbibliothek Zürich',assignment='open')))
    def test_qualifications(self):
        e=p.dated_event(field('Gelangte vermutlich 1832 als Donation von Orelli in den Besitz der Stadtbibliothek Zürich'))
        self.assertEqual((e['year'],e['date_certainty']),(1832,'probable'))
        e=p.dated_event(field('Von Konrad Pellikan um 1540 der Bibliothek des Grossmünsterstifts geschenkt'))
        self.assertEqual((e['year'],e['date_certainty']),(1540,'circa'))
    def test_conflicting_bound_with_dates_not_silently_resolved(self):
        for rid in p.CONFLICTS:
            self.assertIsNone(p.dated_event(field('Gelangte 1836 als Donation in den Besitz der Stadtbibliothek Zürich',rid=rid)))
    def test_dataset_integrity(self):
        ready,pending,reviews,summary=p.build()
        self.assertTrue(ready)
        self.assertEqual(len({r['reference_id'] for r in ready}),len(ready))
        source={p.key(r):r for r in p.read(p.DATA/'working-copy-references.json')}
        for r in ready:
            self.assertIn(p.key(r),source)
            self.assertEqual(r['publication_source'],source[p.key(r)]['publication'])
            origin,event,current=r['stations']
            self.assertLessEqual(origin['year'],event['year'])
            self.assertIsNone(current['acquisition_date'])
            self.assertEqual(current['observed_at'],'2026-10-23')
            self.assertTrue(event['evidence'])
            self.assertIn(event['matched_text'],p.note(event['evidence'][0]))
            for s in r['stations']:
                self.assertTrue(-90<=s['coordinates']['latitude']<=90)
                self.assertTrue(-180<=s['coordinates']['longitude']<=180)
                self.assertTrue(s['coordinate_source']['source_url'].startswith('https://'))
        self.assertEqual(summary['map_ready_station_count'],len(ready)*3)
        self.assertEqual(p.build(),p.build())
    def test_multiple_places_never_collapsed(self):
        a=p.read(ROOT/'data/authority/postincunabula-pilot-places.json')
        self.assertNotIn('[Parisiis et Coloniae]',a['publication_label_map'])

if __name__=='__main__':unittest.main()
