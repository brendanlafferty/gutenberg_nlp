import pickle
import matplotlib.pyplot as plt
import numpy as np
from gensim import models, matutils
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from pre_processing import load_corpus


def iterate_topics(topic_range=range(10, 50, 5), number_of_records=None):
    corpus_list, titles = load_corpus('../texts/gists/', number_of_records=number_of_records)
    with open('../outputs/iter_titles.pkl', 'wb') as fp:
        pickle.dump(titles, fp)
    models = []
    count_vect =  fit_vectorizer(corpus_list)
    corpus, id2word = convert_corpus(corpus_list, count_vect)
    with open('../outputs/iter_corpus.pkl', 'wb') as fp:
        pickle.dump(corpus, fp)
    for num_tops in topic_range:
        lda_loop = fit_lda(num_tops, corpus, id2word, 100, multicore=2, save=True)
        plot_distances(lda_loop, title=f'Differences {num_tops} Topics')
        models.append(lda_loop)
    plot_distances(models[0], title=f'Comparing {topic_range[0]} to {topic_range[-1]} Topics',
                   other_model=models[-1])
    return models


def fit_vectorizer(corpus_list, vec_type='Count', **kwargs):
    """
    Creates a fit vectorizer object from the corpus
    :param corpus_list:
    :param vec_type:
    :return:
    """
    vectorizer_dict = {'count': CountVectorizer, 'tfidf': TfidfVectorizer}
    vectorizer = vectorizer_dict[vec_type.lower()](stop_words='english', **kwargs).fit(corpus_list)
    return vectorizer


def convert_corpus(corpus_list: list, count_vec: CountVectorizer):
    doc_term_mat = count_vec.transform(corpus_list).transpose()
    corpus = matutils.Sparse2Corpus(doc_term_mat)
    id2word = dict((v, k) for k, v in count_vec.vocabulary_.items())
    return corpus, id2word


def fit_lda(num_topics, corpus, id2word, passes, multicore=0, save=True):
    """
    Fits a gensim lda model on the corpus,  Allows for easy switching between single and multicore
    implementations
    :param num_topics: Number of topics to model
    :param corpus: gensim's Sparse2Corpus object
    :param id2word:
    :param passes:
    :param multicore:
    :return:
    """
    if multicore:
        lda_fit = models.LdaMulticore(corpus=corpus, num_topics=num_topics, id2word=id2word,
                                      workers=multicore, passes=passes)
    else:
        lda_fit = models.LdaModel(corpus=corpus, num_topics=num_topics, id2word=id2word,
                                  passes=passes)

    if save:
        lda_fit.save(f'../outputs/lda_{num_topics}_topics.mdl')
    return lda_fit


def plot_distances(lda: models.LdaModel, distance='jaccard', num_words=50, title=None, other_model=None):
    comparison = True
    if not other_model:
        comparison = False
        other_model = lda
    mdiff, annotations = lda.diff(other_model, distance=distance, num_words=num_words)
    topic_difference_heatmap(mdiff=mdiff, title=title, diff_models=comparison)


def topic_difference_heatmap(mdiff, title=None, diff_models=False, dir='../outputs/'):
    """
    Plots the output of gensim's LDA.diff() method.
    It filters out th upper half of the symmetric matrix

    Inspired by https://radimrehurek.com/gensim/auto_examples/howtos/run_compare_lda.html
    :param mdiff: output of lda.diff() from gensim's lda models
    :param title: title for the plot
    :param diff_models: Boolean on whether this is a self comparison or a comparison of different
                        models. If the value is False then the top half of the mdiff array is masked
                        away because if the models are the same the maxtrix is symmetric about above
                        and below the identity matrix
    :return:
    """
    if not title:
        title = 'Topic Differences'
    if not diff_models:
        mask = np.zeros_like(mdiff, dtype=np.bool)
        mask[np.triu_indices_from(mask)] = True
        masked = np.ma.masked_array(mdiff, mask=mask)
    else:
        masked = mdiff

    fig, ax = plt.subplots(figsize=(9, 7))
    data = ax.imshow(masked, cmap='RdYlGn', origin='lower', vmin=0, vmax=1)
    plt.title(title)
    plt.colorbar(data)
    ax.invert_yaxis()

    plt.savefig(f'../outputs/{title}.png', dpi=300)


if __name__ == '__main__':
    # corp_list, titles = load_corpus('../texts/gists/', number_of_records=1500)
    # count_vect = fit_vectorizer(corp_list)
    # corpus, id2word = convert_corpus(corp_list, count_vect)
    # lda = fit_lda(num_topics=10, corpus=corpus, id2word=id2word, passes=100)
    for topics in range(10, 40, 5):
        lda = models.LdaModel.load(f'../outputs/small_dataset_models/lda_{topics}_topics.mdl')
        plot_distances(lda, 'jaccard', 30, f'LDA: Distances Between {topics} Topics')
    # lda.print_topics()
    # iterate_topics(number_of_records=1500)