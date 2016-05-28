__author__ = 'morrj140'
import os
import sys

from nl_lib import Logger
logger = Logger.setupLogging(__name__)
logger.setLevel(Logger.DEBUG)

from gensim import corpora, models, similarities, matutils
from gensim.models import lsimodel

# remove words that appear only once
from collections import defaultdict
from pprint import pprint  # pretty-printer


class MyCorpus(object):
    corpus = None

    def __init__(self, corpusFile):

        if os.path.isfile(corpusFile):
            self.corpus = corpora.MmCorpus(corpusFile)

    def __iter__(self):
        for line in self.corpus:
            # assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())


def ns(numpy_matrix, number_of_corpus_features, scipy_sparse_matrix):
    corpus = matutils.Dense2Corpus(numpy_matrix)

    numpy_matrix = matutils.corpus2dense(corpus, num_terms=number_of_corpus_features)

    corpus = matutils.Sparse2Corpus(scipy_sparse_matrix)
    scipy_csc_matrix = matutils.corpus2csc(corpus)


def dumb_example(dictionary, corpus, index):

        documents = ["Human machine interface for lab abc computer applications",
                     "A survey of user opinion of computer system response time",
                     "The EPS user interface management system",
                     "System and human system engineering testing of EPS",
                     "Relation of user perceived response time to error measurement",
                     "The generation of random binary unordered trees",
                     "The intersection graph of paths in trees",
                     "Graph minors IV Widths of trees and well quasi ordering",
                     "Graph minors A survey"]

        # remove common words and tokenize
        stoplist = set('for a of the and to in'.split())

        texts = [[word for word in document.lower().split() if word not in stoplist] for document in documents]

        frequency = defaultdict(int)

        for text in texts:
            for token in text:
                frequency[token] += 1

                texts = [[token for token in text if frequency[token] > 1] for text in texts]

        pprint(texts)

        d = corpora.Dictionary(texts)

        print(d)

        print(d.token2id)

        corpus = [d.doc2bow(text) for text in texts]

        # remove stop words and words that appear only once
        stop_ids = [d.token2id[stopword] for stopword in stoplist if stopword in d.token2id]

        once_ids = [tokenid for tokenid, docfreq in d.dfs.iteritems() if docfreq == 1]

        # remove stop words and words that appear only once
        d.filter_tokens(stop_ids + once_ids)

        # remove gaps in id sequence after words that were removed
        d.compactify()

        print(dictionary)

        lsi = models.LsiModel(corpus, id2word=d, num_topics=2)

        doc = "Human computer interaction"
        vec_bow = d.doc2bow(doc.lower().split())

        # convert the query to LSI space
        vec_lsi = lsi[vec_bow]
        print(vec_lsi)

        # transform corpus to LSI space and index it
        indexCorpus = similarities.MatrixSimilarity(lsi[corpus])

        # perform a similarity query against the corpus
        print(vec_lsi)
        sims = index[vec_lsi]

        # print (document_number, document_similarity) 2-tuples
        print(list(enumerate(sims)))

        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        # print sorted (document number, similarity score) 2-tuples
        print(sims)

if __name__ == u"__main__":

    nt = 50
    nw = 5

    cwd = os.getcwd()

    df = ("%s/../run/Dictionary.dict" % cwd)
    dictionary = corpora.Dictionary.load(df)

    n = 0
    logger.info("Dictionary[%d]" % (len(dictionary)))
    for k, v in dictionary.items():
        logger.info("%s[%s]" % (k, v))
        n += 1
        if n > nt:
            break

    cf = ("%s/../run/corpus.mm" % cwd)

    corpus = MyCorpus(cf).corpus

    # corpus = corpora.MmCorpus(cf)  # comes from the first tutorial, "From strings to vectors"

    n = 0
    logger.info("corpus[%d]" % (len(corpus)))
    for x in corpus:
        logger.info("%d => %s" % (n, x))
        n += 1
        if n > nt:
            break

    inf = ("%s/../run/corpus.mm.index" % cwd)
    index = similarities.MatrixSimilarity.load(inf)

    n = 0
    logger.info("index[%d]" % (len(index)))
    for x in index:
        logger.info("%d : %s" % (n, x,))
        n += 1
        if n > nt:
            break

    # numpy_matrix = matutils.corpus2dense(corpus, num_terms=nt)

    # logger.info("numpy_matrix[%d]" % (len(index)))
    # for x in numpy_matrix:
    #    logger.info("%s" % x)

    if False:
        dumb_example(dictionary, corpus, index)

    if False:

        lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)

        tfidf = models.TfidfModel(corpus)
        logger.debug(u"tfidf: %s" % str(tfidf))

        corpus_tfidf = tfidf[corpus]
        logger.debug(u"corpus_tfidf: %s" % str(corpus_tfidf))

        # I can print out the topics for LSI
        lsi = lsimodel.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=nt)

        logger.debug(u"LSI Complete")
        corpus_lsi = lsi[corpus]

        logger.debug(u"lsi.print_topics: " + str(lsi.print_topics))

        lsiList = lsi.print_topics(num_topics=nt, num_words=nw)

        n = 0
        for x in lsiList:
            n += 1
            logger.info("%d %s" % (n, x))
