from tqdm.std import TqdmDefaultWriteLock
from pyserini.index import IndexReader
from collections import defaultdict
from nltk.metrics.distance import edit_distance
from tqdm import tqdm, trange
import sys
import os
import numpy as np
import math
import pickle
import pdb


class Ranker(object):
    '''
    The base class for ranking functions. Specific ranking functions should
    extend the score() function, which returns the relevance of a particular 
    document for a given query.
    '''

    def __init__(self, index_reader, docid_ls):
        self.index_reader = index_reader
        self.docid_ls = docid_ls


class PivotedLengthNormalizatinRanker(Ranker):

    def __init__(self, index_reader, docid_ls):
        super(PivotedLengthNormalizatinRanker,
              self).__init__(index_reader, docid_ls)

        self.b = 0.5
        self.docid_ls = docid_ls

        # cal document length and average document length
        self.doclen = defaultdict(int)
        self.docvectors = {}

        for docid in tqdm(self.docid_ls):  # for each document, get doc vector
            doc_vector = self.index_reader.get_document_vector(docid)
            self.docvectors[docid] = doc_vector

        # write pkl
        # name = 'Ranker'
        # pkl_path = os.path.join('DATA/resources/doc_vectors', name + '.pkl')
        # with open(pkl_path, "wb") as file:
        #     pickle.dump(self.docvectors, file)

        # with open(pkl_path, "rb") as file:
        #     self.docvectors = pickle.load(file)

        for docid in docid_ls:  # for each doc, calculate doc length
            self.doclen[docid] = sum(self.docvectors[docid].values())

        self.avg_dl = sum(self.doclen.values()) / len(self.doclen)

    # query = "the hello world"
    def score(self, query):
        '''
        Scores the relevance of the document for the provided query using the
        Pivoted Length Normalization ranking method. Query is a tokenized list
        of query terms and doc_id is a numeric identifier of which document in the
        index should be scored for this query.

        '''
        # Analyze the term
        analyzed_query = self.index_reader.analyze(query)  # ['hello', 'world']
        count_q = defaultdict(int)

        # calculate c(w,q)
        for idx, word in enumerate(analyzed_query):
            count_q[word] += 1

        # cal f(q,d)
        all_score = []
        for docid in tqdm(self.docid_ls):
            rank_score = 0
            DLN = self.calDLN(docid)

            for word in count_q:
                # check if word in whole corpus
                if word in self.docvectors[docid]:
                    IDF = self.calIDF(word)
                    c_wq = self.calc_wq(word, count_q)
                    TF = self.calTF(word, docid)
                    rank_score += c_wq * IDF * TF / DLN

            # print(f'({word}, {docid}) = {c_wq * IDF * TF / DLN}')
            all_score.append([rank_score, docid])

        return all_score

    def calc_wq(self, word, count_q):
        return count_q[word]

    def calTF(self, word, docid):
        doc_vector = self.docvectors[docid]
        if word in doc_vector:
            return 1 + math.log(1 + math.log(doc_vector[word]))
        else:
            return 0

    def calIDF(self, word):
        df = self.index_reader.get_term_counts(word, analyzer=None)[0]
        return math.log((len(self.docid_ls) + 1) / df)

    def calDLN(self, docid):
        return 1 - self.b + self.b * self.doclen[docid] / self.avg_dl


class BM25Ranker(Ranker):

    def __init__(self, index_reader, docid_ls, k1):
        super(BM25Ranker, self).__init__(index_reader, docid_ls)

        self.b = 0.5
        self.k1 = int(k1) * 0.01
        self.k3 = 0.5

        # cal document length and average document length
        self.doclen = defaultdict(int)
        self.docvectors = {}

        for docid in tqdm(self.docid_ls):  # for each document, get doc vector
            doc_vector = self.index_reader.get_document_vector(docid)
            self.docvectors[docid] = doc_vector

        # write pkl
        name = 'Gaming'
        pkl_path = os.path.join('DATA/resources/doc_vectors', name + '.pkl')
        with open(pkl_path, "wb") as file:
            pickle.dump(self.docvectors, file)

        with open(pkl_path, "rb") as file:
            self.docvectors = pickle.load(file)

        for docid in tqdm(self.docid_ls):  # for each doc, calculate doc length
            self.doclen[docid] = sum(self.docvectors[docid].values())

        self.avg_dl = sum(self.doclen.values()) / len(self.doclen)

    def score(self, query):
        '''
        Scores the relevance of the document for the provided query using the
        BM25 ranking method.

        '''
        # Analyze the term
        analyzed_query = self.index_reader.analyze(query)  # ['hello', 'world']
        count_q = defaultdict(int)

        for idx, word in enumerate(analyzed_query):
            count_q[word] += 1

        # cal f(q,d)
        all_score = []
        for docid in tqdm(self.docid_ls):
            rank_score = 0
            DLN = self.calDLN(docid)
            for word in analyzed_query:
                # check if word in whole corpus
                if word in self.docvectors[docid]:
                    IDF = self.calIDF(word)
                    query_term = self.calQuery(count_q[word])
                    TF = self.calTF(word, docid, DLN)
                    rank_score += IDF * TF * query_term
            all_score.append([rank_score, docid])

        return all_score

    def calQuery(self, c_tq):
        return (self.k3 + 1) * c_tq / (self.k3 + c_tq)

    def calTF(self, word, docid, DLN):
        doc_vector = self.docvectors[docid]
        if word in doc_vector:
            return doc_vector[word] * (self.k1 + 1) / (self.k1 * (DLN) + doc_vector[word])
        else:
            return 0

    def calIDF(self, word):
        df = self.index_reader.get_term_counts(word, analyzer=None)[0]
        return math.log((len(self.docid_ls) - df + 0.5) / (df + 0.5))

    def calDLN(self, docid):
        return 1 - self.b + self.b * self.doclen[docid] / self.avg_dl


class MyRanker(Ranker):
    def __init__(self, index_reader, docid_ls, k1):
        super(MyRanker, self).__init__(index_reader, docid_ls)

        self.b = 0.5
        self.k1 = int(k1) * 0.01
        self.k3 = 0.5

        # cal document length and average document length
        self.doclen = defaultdict(int)
        self.docvectors = {}
        self.docvectors['all'] = {}

        # for docid in tqdm(self.docid_ls):  # for each document, get doc vector
        #     doc_vector = self.index_reader.get_document_vector(docid)
        #     self.docvectors[docid] = doc_vector
        #     self.docvectors['all'].update(doc_vector) # self.docvetors['all'] is the dict for the whole corpus

        # write pkl
        name = 'Android'
        pkl_path = os.path.join('DATA/resources/doc_vectors', name + '.pkl')
        # with open(pkl_path, "wb") as file:
        #     pickle.dump(self.docvectors, file)

        with open(pkl_path, "rb") as file:
            self.docvectors = pickle.load(file)

        for docid in tqdm(self.docid_ls):  # for each doc, calculate doc length
            self.doclen[docid] = sum(self.docvectors[docid].values())

        self.avg_dl = sum(self.doclen.values()) / len(self.doclen)
        self.threshold = 0.3

    def score(self, query):
        '''
        Scores the relevance of the document for the provided query using the
        My ranking method.

        '''
        # Analyze the term
        analyzed_query = self.index_reader.analyze(query)  # ['hello', 'world']
        count_q = defaultdict(int)

        for idx, word in enumerate(analyzed_query):
            if word in self.docvectors['all']:
                count_q[word] += 1
            else:  # find the closest word that's in the doc vector
                newword = self.calSimilarity(word)
                if newword:
                    count_q[newword] += 1

        # cal f(q,d)
        all_score = []
        for docid in tqdm(self.docid_ls):
            rank_score = 0
            DLN = self.calDLN(docid)
            for word in count_q:
                # check if word in whole corpus
                if word in self.docvectors[docid]:
                    IDF = self.calIDF(word)
                    query_term = self.calQuery(count_q[word])
                    TF = self.calTF(word, docid, DLN)
                    rank_score += IDF * TF * query_term
            all_score.append([rank_score, docid])

        return all_score

    def calQuery(self, c_tq):
        return (self.k3 + 1) * c_tq / (self.k3 + c_tq)

    def calTF(self, word, docid, DLN):
        doc_vector = self.docvectors[docid]
        if word in doc_vector:
            return doc_vector[word] * (self.k1 + 1) / (self.k1 * (DLN) + doc_vector[word])
        else:
            return 0

    def calIDF(self, word):
        df = self.index_reader.get_term_counts(word, analyzer=None)[0]
        return (math.log((len(self.docid_ls) - df + 0.5) / (df + 0.5)))

    def calDLN(self, docid):
        return 1 - self.b + self.b * self.doclen[docid] / self.avg_dl

    def calSimilarity(self, word):  # return the closest word that's in the corpus
        for key, value in self.docvectors['all'].items():
            simscore = (edit_distance(word, key)) / len(word)
            if simscore < self.threshold:
                print(
                    f'simscore: {simscore}, key: {key}, value: {value}, editdistance: {edit_distance(word, key)} word: {(word)}')
                return key
        print(f'no similar')
        return 0
