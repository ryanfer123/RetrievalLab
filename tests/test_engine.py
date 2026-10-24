import copy
import json
import math
from pathlib import Path
import unittest

from retrieval_lab.engine import Index, compare, metrics, validate_dataset

DEMO = json.loads((Path(__file__).parents[1]/'retrieval_lab/web/demo.json').read_text())


class EngineTests(unittest.TestCase):
    def test_metrics_match_hand_calculation(self):
        result = metrics(['wrong', 'a', 'b'], ['a', 'b'], 3)
        self.assertAlmostEqual(result['precision'], 2/3)
        self.assertEqual(result['recall'], 1)
        self.assertEqual(result['mrr'], .5)
        self.assertAlmostEqual(result['ndcg'], (1/math.log2(3)+.5)/(1+1/math.log2(3)))

    def test_missing_results_reduce_precision(self):
        self.assertEqual(metrics(['a'], ['a'], 5)['precision'], .2)

    def test_cutoff_does_not_count_later_hits(self):
        self.assertEqual(metrics(['wrong', 'a'], ['a'], 1)['mrr'], 0)

    def test_metrics_reject_undefined_and_duplicate_inputs(self):
        for args in [(['a','a'], ['a'], 3), ([], [], 3), ([], ['a'], 0)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                metrics(*args)

    def test_exact_match_outranks_irrelevant_document(self):
        index = Index([{'id':'a','text':'battery health'},{'id':'b','text':'food delivery'}])
        for method in ('bm25', 'tfidf'):
            self.assertEqual(index.search('battery', method, 2)[0]['id'], 'a')
            self.assertEqual(index.search('unmatchedvocabulary', method, 2), [])

    def test_ties_are_deterministic_by_id(self):
        index = Index([{'id':'z','text':'same text'},{'id':'a','text':'same text'}])
        for method in ('bm25','tfidf'):
            self.assertEqual([x['id'] for x in index.search('text', method, 2)], ['a','z'])

    def test_bm25_matches_reference_formula(self):
        index = Index([{'id':'a','text':'cat cat'},{'id':'b','text':'dog'}])
        expected = math.log(2) * 2 * 2.5 / (2 + 1.5*(.25+.75*2/1.5))
        self.assertAlmostEqual(index.search('cat','bm25',2)[0]['score'], expected)

    def test_tfidf_identical_vector_has_unit_cosine(self):
        index = Index([{'id':'a','text':'cat dog'}])
        self.assertAlmostEqual(index.search('cat dog','tfidf',1)[0]['score'],1)

    def test_compare_reports_both_methods_and_stable_hash(self):
        result = compare(DEMO, 3)
        self.assertEqual(set(result['methods']), {'bm25','tfidf'})
        self.assertEqual(len(result['queries']), 5)
        self.assertEqual(result['dataset_sha256'], compare(DEMO,3)['dataset_sha256'])
        for method in result['methods'].values():
            for key in ('precision','recall','mrr','ndcg'):
                self.assertTrue(0 <= method[key] <= 1)

    def test_bad_dataset_rejected_before_indexing(self):
        cases = [None, {}, {'name':'x','documents':[], 'queries':[]}]
        for mutation in ('duplicate', 'unknown-relevance', 'empty-text', 'bad-id', 'no-labels'):
            data = copy.deepcopy(DEMO)
            if mutation == 'duplicate': data['documents'].append(data['documents'][0])
            if mutation == 'unknown-relevance': data['queries'][0]['relevant_ids']=['unknown']
            if mutation == 'empty-text': data['documents'][0]['text']='!!!'
            if mutation == 'bad-id': data['queries'][0]['id']=0
            if mutation == 'no-labels': data['queries'][0]['relevant_ids']=[]
            cases.append(data)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_dataset(data)

    def test_cutoff_validated(self):
        for k in (0,21,True,1.5,'5'):
            with self.subTest(k=k), self.assertRaises(ValueError):
                compare(DEMO,k)
