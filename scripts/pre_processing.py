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


def corpus_cleaning(corpus, tokenizer, stemmer):
    cleaned_text = []
    for document in corpus:
        cleaned_words = []
        for word in tokenizer.tokenize(document):
            low_word = word.lower()
            if stemmer:
                low_word = stemmer.stem(low_word)
            cleaned_words.append(low_word)
        cleaned_text.append(' '.join(cleaned_words))
    #cleaned_text = corpus
    return cleaned_text


def gistify(input_dir, output_dir):
    corpus, titles = load_corpus(input_dir, output_dir)
    print('\n\t\t', len(corpus))
    for ind, book in enumerate(corpus):
        logging.debug(f'Attempting to Gistify: {titles[ind]}')
        gist, gist_token = create_gist(book)
        logging.debug('\tSaving gist')
        save_gist(output_dir, titles[ind], gist)


def create_gist(document, gist_depth=1000):
    clean_tokens = gist_pre_processing(document)
    top_words = get_top_words(clean_tokens, gist_depth)

    gist, gist_tokens = filter_to_gist(clean_tokens, top_words)

    return gist, gist_tokens


def gist_pre_processing(document):
    punct = "".join(punctuation.split("'"))  # leave apostrophes
    no_punctuation = re.sub(f'[{re.escape(punct)}]', ' ', document)
    no_nums_no_punc = re.sub('\w*\d\w*', ' ', no_punctuation)
    clean_tokens = word_tokenize(no_nums_no_punc.lower())

    return clean_tokens


def get_top_words(tokens, num):
    word_counts = Counter(tokens)
    top_n_words = [item[0] for item in word_counts.most_common(num)]
    return top_n_words


def filter_to_gist(tokens, words_to_keep):
    gist_tokens = []
    for word in tokens:
        if word in words_to_keep:
            gist_tokens.append(word)
    gist = ' '.join(gist_tokens)
    return gist, gist_tokens


def save_gist(directory, file_title, gist, extension='.txt'):
    file_path = os.path.join(directory, file_title) + extension
    with open(file_path, 'w') as fp:
        fp.write(gist)


def gist_exists(directory, title, extension='.txt'):
    file_path = os.path.join(directory, title) + extension
    return os.path.exists(file_path)


if __name__ == '__main__':
    gistify('../texts/', '../texts/gists')


