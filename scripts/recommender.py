"""
Module for recommending project gutenberg books

"""


import pickle
import sys
import os.path as path
import pandas as pd
from gutenberg.query.api import get_metadata
from sklearn.metrics import pairwise_distances
import joblib
from gensim.models import LdaMulticore
from typing import List


_CURRENT_MODEL = 'lda_30_topics.mdl'
_CURRENT_CORPUS = 'iter_corpus.pkl'
_CURRENT_TITLES = 'iter_topics.pkl'
_RELATIVE_DIR = '../outputs/small_dataset_models'


def recommender(book_id: int = None, number_of_recommendations: int = None,
                resources: tuple = None):
    """
    Main Book Recommender
    :param book_id: the gutenberg id of the book to make recommendations from
    :param number_of_recommendations: the number of recommendations to make
    :param resources: this optional parameter helps performance by keeping the resources in memory
                      between recommendations
    :return: the number of recommendations requested based upon the book
    """
    if not resources:
        resources = load_resources()
    if not book_id:
        book_id = poll_user('What book did you like?\nid: ')
    starting_metadata = concat_metadata([book_id])
    print_metadata(starting_metadata)
    if not number_of_recommendations:
        number_of_recommendations = poll_user('How many similar books would you like to see?\n#: ')
    recommendations = recommend(book_id, number_of_recommendations, resources)
    print('Recommendations')
    print_metadata(recommendations)
    pause()
    return recommendations


def recommend(book_id, num_recs, resources = None):
    """
    manages creating the recommendation
    :param book_id: book to recommend from
    :param num_recs: number of recommendations to make
    :param resources: these are the pickled
    :param metric:
    :return:
    """
    if not resources:
        resources = load_resources()
    model, corpus, ids, pg_id_to_ind, dist_mat = resources
    ind = pg_id_to_ind[book_id]

    trans_corpus = model.get_document_topics(corpus)
    topic_weights = [doc for doc in trans_corpus]
    doc_to_tops = topic_weights_to_matrix(topic_weights)

    rec_ind = similar_ids(ind, doc_to_tops, num_recs, dist_mat)
    rec_ids = [ids[ind] for ind in rec_ind]
    recommendations = concat_metadata(rec_ids)

    return recommendations


def load_resources():
    """
    loads all of the serialize objects for the recommender to work.  Books identifies exist in
    realms: there is the gutenberg book id and the index where the book exsists in the corpus.
    These are not identical.

    :return: model object, corpus vects object, list of gutenberg ids,
             dictionary of book index number to id
    """
    model = LdaMulticore.load(path.join(_RELATIVE_DIR, _CURRENT_MODEL))
    corpus = _unpickle(path.join(_RELATIVE_DIR, _CURRENT_CORPUS))
    ids = _unpickle(path.join(_RELATIVE_DIR, _CURRENT_TITLES))
    ids_to_ind_dict = {int(id_loop): ind_loop for ind_loop, id_loop in enumerate(ids)}
    distance_mat_location = path.join(_RELATIVE_DIR, _CURRENT_MODEL + '.distance_matrix.pkl')
    if path.isfile(distance_mat_location):
        dist_mat = _unpickle(distance_mat_location, True)
    else:
        dist_mat = None
    return model, corpus, ids, ids_to_ind_dict, dist_mat


def similar_ids(document_index, doc_topics, num_recs=1, distance_mat=None):
    """
    This function calculates distances to minimize for the recommendation
    :param document_index: the index of the book from which the recommendation is based [index not
                           gutenberg id]
    :param doc_topics: document topics matrix
    :param num_recs: how many recomendations to make
    :return: a list of the recommendations
    """
    if distance_mat is None:
        pkl_local = path.join(_RELATIVE_DIR, _CURRENT_MODEL + '.distance_matrix.pkl')
        if path.isfile(pkl_local):
            distance_mat = _unpickle(pkl_local, True)
        else:
            distance_mat = pairwise_distances(doc_topics.values, metric='cosine')
            _pickle(pkl_local, distance_mat, True)
    recs = distance_mat[document_index].argsort()
    return recs[1:1 + num_recs]


def topic_weights_to_matrix(topic_weights, doc_ids=None, topic_ids=None):
    """
    converts the output of gensim topic weights to a proper document to topic matrix
    :param topic_weights: List[List[Tuples[Topic, Topic Probability]]]
    :param doc_ids: (optional) list of document titles/ids in the same order as the topic_weights
                    if provided this will change the index to the document titles/ids
    :param topic_ids: (optional) list of topic names. if provided this will change the columns to
                      the topic names
    :return: panda data frame of the document to topic matrix
    """
    topic_dicts = [dict(doc) for doc in topic_weights]
    doc_to_top_mat = pd.DataFrame(topic_dicts).fillna(0)
    if doc_ids:
        doc_to_top_mat.rename(index=lambda ind: doc_ids[ind], inplace=True)
    if topic_ids:
        doc_to_top_mat.rename(columns=lambda ind: topic_ids[ind], inplace=True)
    return doc_to_top_mat


def concat_metadata(ids: List[int]):
    """
    compiles the metadata from a book id
    :param ids: list of gutenberg ids to fetch metadata form
    :return: list of tuples of book id, title, author, and  link to website
    """
    metadata = []
    for book_id in ids:
        title = get_title(book_id)
        author = get_author(book_id)
        link = f'https://www.gutenberg.org/ebooks/{book_id}'
        metadata.append((book_id, title, author, link))
    return metadata


def get_title(book_id: int):
    """
    Returns the title of the given book id
    :param book_id: gutenberg id
    :return: the book's title in a string
    """
    return _get_attr(book_id, 'title')


def get_author(book_id):
    """
    Returns the author of the given book id
    :param book_id: gutenberg id
    :return: the book's author in a string
    """
    return _get_attr(book_id, 'author')


def _get_attr(book_id: int, attr: str):
    """
    interface with the gutenberg python library.  The library returns frozen sets so this code
    extracts the attributes and returns them as a string
    :param book_id: gutenbern id
    :param attr:
    :return:
    """
    # res, *bla = get_metadata(attr, book_id)
    res = ':('
    res = res.split('\n')[0]
    if len(res) > 50:
        res = res[:50]
    return res


def _unpickle(file_path, use_joblib=False):
    with open(file_path, 'rb') as fp:
        if use_joblib:
            return joblib.load(fp)
        return pickle.load(fp)


def _pickle(file_path, obj, use_joblib=False):
    with open(file_path, 'wb') as fp:
        if use_joblib:
            joblib.dump(obj, fp)
        else:
            pickle.dump(obj, fp)


def poll_user(message):
    valid = False
    while not valid:
        res = input(message)
        try:
            gutenberg_id = int(res)
        except ValueError:
            print('Please enter an integer')
        else:
            return gutenberg_id


def print_metadata(metadata):
    format_str = '{:>7} | {:^50s} | {:^50s} | {:<40}'
    print(format_str.format('ID', 'Title', 'Author', 'link'))
    print('—' * 156)
    for entry in metadata:
        print(format_str.format(*entry))


def pause():
    """
    Pauses for user input
    :return: None
    """
    input('Press Return to Continue:\nEnter')


def print_directions():
    """
    Quick function to give directions to the user
    :return:
    """
    directions = \
        '''Welcome to a project gutenberg recommendation system\n''' + \
        '''Please find a book you liked on project gutenberg's website:\n''' + \
        '''\t https://www.gutenberg.org/\n''' + \
        '''Once you find one copy the book id. To find the book id look at the numbers \n''' +\
        '''at the end of the url:\n''' + \
        '''E.G. The Picture of Dorian Gray by Oscar Wilde is found here:\n''' + \
        '''\t https://www.gutenberg.org/ebooks/174\n''' + \
        '''The id is 174'''
    print(directions)


def main():
    """
    Runs a loop of recommendations.  Can accept system arguments.
    pattern:
        $ python recommender.py <book id> <number of recommendations>
    e.g.
        $ python recommender.py 3888 5

    :return:
    """
    print_directions()
    resources = load_resources()
    # allows sys args
    args = [int(arg) for arg in sys.argv[1:]]
    while True:
        try:
            recommender(*args, resources=resources)
        except KeyboardInterrupt:
            print('\nquitting')
            break
        else:
            # after the first iteration delete passed arguments.
            if args:
                args = []


if __name__ == '__main__':
    main()
