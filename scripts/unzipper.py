import os
from sys import argv
from zipfile import ZipFile
import logging


def unzip(import_directory: str = './', export_directory: str = './', extension: str = '.zip'):
    logging.debug(f'import dir: {import_directory}\n'
                  f'export_dir: {export_directory}\n'
                  f'file ext: {extension}')
    for item in os.listdir(import_directory):
        if item.endswith(extension):
            logging.info(f'unzipping: {item}')
            path = import_directory + item
            with ZipFile(path) as zipped:
                zipped.extractall(path=export_directory)
            os.remove(path)


if __name__ == '__main__':
    unzip(*argv[1:])
