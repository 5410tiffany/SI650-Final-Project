from rankers import BM25Ranker, PivotedLengthNormalizatinRanker, MyRanker
from pyserini.index import IndexReader
from tqdm import tqdm, trange
import sys
import pandas as pd
import pdb


def single_query(index_reader, ranker, query, k):
    '''
    Find the relevant documents given query
    '''
    all_score = ranker.score(query)
    all_score.sort(reverse=True)
    for item in all_score[:5]:
        id = item[1]
        rawdata = index_reader.doc_raw(id)
        print(rawdata)
        print('-----')

    # dids = [item[1] for item in all_score[:5]]
    # print(dids)


def run_test(ranker, path, output_fname):
    '''
    Prints the relevance scores of the top retrieved documents.
    '''
    queryid = []
    docid = []
    df = pd.read_csv(path)
    # df = df[:2]
    for index, row in df.iterrows():
        # print(row)
        all_score = ranker.score(row['Query Description'])
        all_score.sort(reverse=True)

        did = [item[1] for item in all_score[:5]]
        qid = [row['QueryId'] for item in range(5)]

        docid += did
        queryid += qid

    data = {'QueryId': queryid, 'DocumentId': docid}
    submission_df = pd.DataFrame(data=data)
    submission_df.to_csv(output_fname, index=False)


def get_docid_ls(path):
    df = pd.read_csv(path)
    df = df.dropna()
    ls = [str(row['DocumentId']) for index, row in df.iterrows()]

    print(f'docls length: {len(ls)}')
    return ls


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("usage: python main.py <index file paths> <query> ")
        exit(1)

    # NOTE: You should already have used pyserini to generate the index files
    # before calling main
    index_fname = sys.argv[1]  # index json file
    # doc_fname = sys.argv[2]
    doclen = 16  # how many documents are there
    query = sys.argv[2]  # query
    # query_fname = sys.argv[3]
    # k1 = sys.argv[4] # k1

    index_reader = IndexReader.from_prebuilt_index('robust04')
    index_reader = IndexReader(index_fname)  # Reading the indexes
    # pdb.set_trace()
    # docid_ls = get_docid_ls(doc_fname)
    docid_ls = [str(i) for i in range(doclen)]

    # index_reader.doc

    # print(docid_ls)

    # Print some basic stats
    print("Loaded dataset with the following statistics: " +
          str(index_reader.stats()))

    print("Initializing Ranker")
    # Choose which ranker class you want to use
    # ranker = BM25Ranker(index_reader, docid_ls, k1)
    ranker = PivotedLengthNormalizatinRanker(index_reader, docid_ls)
    # ranker = MyRanker(index_reader, docid_ls, 100)
    print("Tesing Ranker!")
    # output_fname = f'output-{k1}.csv'
    # run_test(ranker, query_fname, output_fname)
    single_query(index_reader, ranker, query, 5)
