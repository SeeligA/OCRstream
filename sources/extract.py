import os
import shutil
import csv
import logging

from sources.config import TOP_DIR, PROJECT_DATABASE_EXPORT, clients_dict, source_root
from sources.utils import copy_dirs


def extract_source_files():
    """
    Copy project source files listed in TW export to target directory (TOP DIR)

    Returns:
        cache -- Dictionary mapping project folder names to source language ids
    """

    # Clear target directory if it already exists.
    # IMPORTANT: The second condition prevents you from accidentally deleting data not on C:
    if os.path.exists(TOP_DIR) and os.path.splitdrive(TOP_DIR)[0] == 'C:':
        shutil.rmtree(TOP_DIR)
        logging.info('{} has been removed'.format(TOP_DIR))

    # Process projects entries in CSV line per line
    with open(PROJECT_DATABASE_EXPORT, newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
        cache = dict()

        #  TODO: Replace the following strings with the corresponding column names in you PROJECT_DATABASE_EXPORT file
        client_col = 'adressID'
        prj_col = 'projektNr'
        lid_col = 'D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'

        for row in datareader:

            # Check addressID value against keys in client dictionary
            client = clients_dict.get(row[client_col], None)
            if client:

                # Build paths for source and target directories from TW data
                # Example Source: L:\ORDER_DIRECTORY\CLIENT 123456\03_Projekte\XXXXXX-123456\01_Orig
                # Example Target: C:\Users\seelig\extract\CLIENT 123456\XXXXXX-123456
                project_folder = '{}-{}'.format(row[prj_col], row[client_col])

                # Note: This hack is only suitable for Windows. Use os.path.join() or pathlib for proper path handling.
                #  TODO: Replace "03_Projekte" and "01_Orig" with the folders relevant to your file directory
                source_dir = '{}\\03_Projekte\\{}\\01_Orig'.format(client, project_folder)
                target_dir = '{}\\{}'.format(client, project_folder)

                src = os.path.join(source_root, source_dir)
                dst = os.path.join(TOP_DIR, target_dir)

                # Call utility function to copy 01_Orig files to target path
                copy_dirs(src, dst)

                # We store the source language ID to use it as a parameter in the retrieve_lid call during ocr
                cache[project_folder] = [client, row[lid_col][:-2]]

    return cache
