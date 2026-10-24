"""Deterministic lexical baselines and binary relevance evaluation."""
from collections import Counter
import hashlib
import json
import math
import re
import time


def tokens(text):
    return re.findall(r'[^\W_]+', text.casefold())


def canonical_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def validate_dataset(data):
    if not isinstance(data, dict):
        raise ValueError('Dataset must be a JSON object.')
    name = data.get('name')
    if not isinstance(name, str) or not name.strip() or len(name) > 120:
        raise ValueError('Name must contain 1 to 120 characters.')
    documents, queries = data.get('documents'), data.get('queries')
    if not isinstance(documents, list) or not 1 <= len(documents) <= 1000:
        raise ValueError('Provide 1 to 1,000 documents.')
    if not isinstance(queries, list) or not 1 <= len(queries) <= 100:
        raise ValueError('Provide 1 to 100 queries.')
    cleaned = {'name': name.strip(), 'documents': [], 'queries': []}
    for key, rows in [('documents', documents), ('queries', queries)]:
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f'Each {key} entry must be an object.')
            identifier, text = row.get('id'), row.get('text')
            if not isinstance(identifier, str) or not identifier.strip() or len(identifier) > 80 or identifier in seen:
                raise ValueError(f'Each {key} ID must be a unique nonempty string up to 80 characters.')
            if not isinstance(text, str) or not tokens(text) or len(text) > 10000:
                raise ValueError(f'Each {key} text must contain words and be at most 10,000 characters.')
            seen.add(identifier)
            cleaned[key].append({'id': identifier, 'text': text})
    doc_ids = {d['id'] for d in cleaned['documents']}
    for source, query in zip(queries, cleaned['queries']):
        relevant = source.get('relevant_ids')
        if not isinstance(relevant, list) or not relevant or any(not isinstance(x, str) for x in relevant):
            raise ValueError('Each query needs a nonempty relevant_ids list of document IDs.')
        if len(set(relevant)) != len(relevant) or not set(relevant) <= doc_ids:
            raise ValueError('Relevance IDs must be unique and reference existing documents.')
        query['relevant_ids'] = sorted(relevant)
    return cleaned


class Index:
    def __init__(self, documents):
        self.documents = documents
        self.counts = [Counter(tokens(d['text'])) for d in documents]
        self.df = Counter(term for count in self.counts for term in count)
        self.lengths = [sum(count.values()) for count in self.counts]
        self.average_length = sum(self.lengths) / len(documents)
        self.idf = {t: math.log((len(documents) + 1) / (freq + 1)) + 1 for t, freq in self.df.items()}
        self.vectors = [{t: (1 + math.log(tf)) * self.idf[t] for t, tf in c.items()} for c in self.counts]
        self.norms = [math.sqrt(sum(v*v for v in vec.values())) for vec in self.vectors]

    def search(self, query, method, k):
        if method not in ('bm25', 'tfidf'):
            raise ValueError('Unknown retrieval method.')
        query_counts = Counter(tokens(query))
        query_vector = {t: (1 + math.log(tf)) * self.idf[t] for t, tf in query_counts.items() if t in self.idf}
        query_norm = math.sqrt(sum(v*v for v in query_vector.values()))
        results = []
        for i, document in enumerate(self.documents):
            score = 0.0
            if method == 'bm25':
                for term in query_counts:
                    tf = self.counts[i][term]
                    if tf:
                        idf = math.log(1 + (len(self.documents)-self.df[term]+0.5)/(self.df[term]+0.5))
                        score += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75*self.lengths[i]/self.average_length))
            elif query_norm:
                score = sum(weight*self.vectors[i].get(t, 0) for t, weight in query_vector.items()) / (query_norm*self.norms[i])
            if score > 0:
                results.append({'id': document['id'], 'text': document['text'], 'score': score})
        return sorted(results, key=lambda r: (-r['score'], r['id']))[:k]


def metrics(ranked_ids, relevant_ids, k):
    if type(k) is not int or k < 1:
        raise ValueError('k must be a positive integer.')
    if len(set(ranked_ids)) != len(ranked_ids):
        raise ValueError('Ranked document IDs must be unique.')
    relevant = set(relevant_ids)
    if not relevant:
        raise ValueError('At least one relevant document is required.')
    hits = [identifier in relevant for identifier in ranked_ids[:k]]
    dcg = sum(hit/math.log2(rank+2) for rank, hit in enumerate(hits))
    ideal = sum(1/math.log2(rank+2) for rank in range(min(k, len(relevant))))
    return {
        'precision': sum(hits)/k,
        'recall': sum(hits)/len(relevant),
        'mrr': next((1/(rank+1) for rank, hit in enumerate(hits) if hit), 0.0),
        'ndcg': dcg/ideal,
    }


def compare(dataset, k=5):
    dataset = validate_dataset(dataset)
    if type(k) is not int or not 1 <= k <= 20:
        raise ValueError('k must be an integer from 1 to 20.')
    index = Index(dataset['documents'])
    result = {'k': k, 'dataset_sha256': hashlib.sha256(canonical_json(dataset).encode()).hexdigest(),
              'configuration': {
                  'tokenizer': 'Unicode words, casefold, no stemming or stopword removal',
                  'bm25': {'k1': 1.5, 'b': 0.75, 'idf': 'log(1 + (N-df+0.5)/(df+0.5))'},
                  'tfidf': {'tf': '1 + log(count)', 'idf': 'log((N+1)/(df+1)) + 1', 'similarity': 'cosine'},
                  'relevance': 'binary', 'ties': 'document ID ascending',
              },
              'methods': {}, 'queries': []}
    for query in dataset['queries']:
        entry = dict(query, results={})
        for method in ('bm25', 'tfidf'):
            start = time.perf_counter()
            ranking = index.search(query['text'], method, k)
            elapsed_ms = (time.perf_counter()-start)*1000
            entry['results'][method] = {'ranking': ranking, 'latency_ms': elapsed_ms,
                'metrics': metrics([r['id'] for r in ranking], query['relevant_ids'], k)}
        result['queries'].append(entry)
    for method in ('bm25', 'tfidf'):
        rows = [q['results'][method] for q in result['queries']]
        result['methods'][method] = {metric: sum(r['metrics'][metric] for r in rows)/len(rows)
                                     for metric in ('precision', 'recall', 'mrr', 'ndcg')}
        result['methods'][method]['mean_latency_ms'] = sum(r['latency_ms'] for r in rows)/len(rows)
    return result
