import os
from sys import argv
import logging


def clean_directories(directory: str = './'):
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            os.rmdir(item_path)

        except NotADirectoryError:
            logging.debug(f'{item_path} is not a directory')

        except OSError:
            logging.debug(f'{item_path} is not empty')

        else:
            logging.info(f'{item} successfully removed')


if __name__ == '__main__':
    clean_directories(*argv[1:])
