import os
import shutil
from sources.utils import copy_files

BASE_DIR = os.getcwd()
TOP_DIR = "C:\\Users\\seelig\\extract\\"
CORPUS_DIR = "C:\\Users\\seelig\\test_corpus\\"


def load_to_corpus():
    for root, dirs, files in os.walk(TOP_DIR):
        for file in filter(lambda file: file.lower().endswith('.txt'), files):

            src = os.path.join(root, file)
            dst = os.path.join(CORPUS_DIR, os.path.basename(root))

            copy_files(src, dst)


if __name__ == '__main__':
    load_to_corpus()