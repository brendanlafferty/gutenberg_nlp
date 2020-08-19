import os
from sys import argv
import logging
from gutenberg.cleanup.strip_headers import strip_headers


def strip_headers_dir(directory: str = './', extension: str = '.txt'):
    for item in os.listdir(directory):
        if item.endswith(extension):
            path = os.path.join(directory, item)
            try:
                # there seem to be a number of odd characters that were mis-encoded so setting
                # errors to ignore will leave those characters out. The files are supposed to ascii
                # but there seems to be a few that are not
                with open(path, 'r+', errors='ignore') as file:
                    text = file.read()

            except IsADirectoryError:
                logging.debug(f'{item} is a directory')

            else:
                clean_text = strip_headers(text)
                with open(path, 'r+') as file:
                    file.write(clean_text)
                    file.truncate()
                logging.debug(f'{item} truncated')


if __name__ == '__main__':
    strip_headers_dir(*argv[1:])
