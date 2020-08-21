import os
import sys
import re
import logging
from collections import Counter
from typing import List
from string import punctuation

from nltk.tokenize import word_tokenize

Corpus = List[str]

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.DEBUG)


def load_corpus(directory: str = './', skip_dir: str = '', number_of_records: int = None):
    """
    this is a workhorse of a function.  It loads the data from the specified directory and has ways
    to limit what gets loaded so that the whole corpus doesn't get loaded every time for every thing
    for creating gists the output directory can be specified so that if gists already exist they can
    be skipped, also a hard limit to the number of documents can be set.
    :param directory: directory to load all .txt files from
    :param skip_dir: if a file of the same name appears in this directory then it will not be loaded
    :param number_of_records: hard limit on the number of documents to load
    :return:
    """
    corpus = []
    indexing = []
    try:
        skip_list = os.listdir(skip_dir)
    except FileNotFoundError:
        skip_list = []
    skip_list.extend(['.DS_Store'])
    dir_contents = os.listdir(directory)
    if not number_of_records:
        number_of_records = len(dir_contents)
    for file in dir_contents:
        if file in skip_list:
            continue
        file_path = os.path.join(directory, file)
        logging.debug(f'Attempting to open {file_path}')
        try:
            with open(file_path, 'r') as file_stream:
                corpus.append(file_stream.read())
        except IsADirectoryError:
            logging.debug(f'{file_path} is a directory')
        else:
            indexing.append(file[:-4])
            if len(indexing) >=  number_of_records:
                break

    return corpus, indexing



def gistify(input_dir: str, output_dir: str):
    """
    main function that oversees creating gists of the corpus.  The function skips any files that
    already appear in the output directory.
    :param input_dir: directory containing the raw text files
    :param output_dir: directory to save the gist text files
    :return: None
    """
    corpus, titles = load_corpus(input_dir, output_dir)
    print('\n\t\t', len(corpus))
    for ind, book in enumerate(corpus):
        logging.debug(f'Attempting to Gistify: {titles[ind]}')
        gist, gist_token = create_gist(book)
        logging.debug('\tSaving gist')
        save_gist(output_dir, titles[ind], gist)


def create_gist(document: str, gist_depth: int = 1000):
    """

    :param document:
    :param gist_depth:
    :return: gist and tokenized gist
    """
    clean_tokens = gist_pre_processing(document)
    top_words = get_top_words(clean_tokens, gist_depth)

    gist, gist_tokens = filter_to_gist(clean_tokens, top_words)

    return gist, gist_tokens


def gist_pre_processing(document: str):
    """
    cleaning and tokenizing function. removes numbers and punctuation except ' as they will be
    helpful in identifying stop words later
    :param document: string
    :return: cleaned tokens of the document
    """
    punct = "".join(punctuation.split("'"))  # leave apostrophes
    no_punctuation = re.sub(f'[{re.escape(punct)}]', ' ', document)
    no_nums_no_punc = re.sub('\w*\d\w*', ' ', no_punctuation)
    clean_tokens = word_tokenize(no_nums_no_punc.lower())

    return clean_tokens


def get_top_words(tokens: list, num: int):
    """
    returns a list of the top so many words that appear in the document
    :param tokens: tokenized document
    :param num: number of top words to return
    :return: list of words in the top num of the document
    """
    word_counts = Counter(tokens)
    top_n_words = [item[0] for item in word_counts.most_common(num)]
    return top_n_words


def filter_to_gist(tokens: list, words_to_keep: list):
    """
    filters the tokenized document down to only specified words
    :param tokens: list of tokens
    :param words_to_keep: list of tokens to keep
    :return: gist and tokenized gist
    """
    gist_tokens = []
    for word in tokens:
        if word in words_to_keep:
            gist_tokens.append(word)
    gist = ' '.join(gist_tokens)
    return gist, gist_tokens


def save_gist(directory: str, file_title: str, gist, extension: str = '.txt'):
    """
    Wrapper around python's i/o to save the contents of the file
    :param directory: place to save to
    :param file_title: title to give to the file
    :param gist: the data to save to the file
    :param extension: file extension, defaults to .txt
    :return:
    """
    file_path = os.path.join(directory, file_title) + extension
    with open(file_path, 'w') as fp:
        fp.write(gist)


def gist_exists(directory: str, title: str, extension: str = '.txt'):
    """
    checks to see if there is a properly named file already existing in the directory
    :param directory: directory to check
    :param title: the title of the file
    :param extension: the file extension, defaults to .txt
    :return: boolean whether the file exists
    """
    file_path = os.path.join(directory, title) + extension
    return os.path.exists(file_path)


if __name__ == '__main__':
    gistify('../texts/', '../texts/gists')


