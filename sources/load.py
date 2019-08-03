import os

from sources.utils import copy_files
from sources.config import TOP_DIR, CORPUS_TEMP


def load_to_corpus(cache):
    for root, dirs, files in os.walk(TOP_DIR):
        for file in filter(lambda file: file.lower().endswith('.txt'), files):

            src = os.path.join(root, file)
            # Extract project folder from path
            project_folder = os.path.basename(root)
            # Lookup client folder in cache dictionary
            client_folder = cache.get(project_folder, None)[0]

            dst = os.path.join(CORPUS_TEMP, os.path.join(client_folder, project_folder))

            copy_files(src, dst)
