import os
import csv

from sources.config import TOP_DIR, clients_dict, SOURCE_ROOT
from sources.utils import copy_dirs, delete_dir


def extract_source_files(PROJECT_DATABASE_EXPORT):
    """Copy project source files listed in TW export to target directory (TOP DIR).

    Arguments:
        PROJECT_DATABASE_EXPORT -- Path to pre-processed CSV data from ERP export

    The function checks client IDs in the export data against the client_dict.
    If there is a match, it tries to build a path from project ID data and client ID data.
    If it generates a valid path, the folder for incoming files is copied to the staging folder.

    Returns:
        cache -- Dictionary mapping project folder names to client names and source language IDs
    """
    # Clear local target directory if it already exists
    delete_dir(TOP_DIR)

    # Process projects entries in CSV line per line
    with open(PROJECT_DATABASE_EXPORT, newline='') as csvfile:
        datareader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
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

                src = os.path.join(SOURCE_ROOT, source_dir)
                dst = os.path.join(TOP_DIR, target_dir)

                # Call utility function to copy 01_Orig files to target path
                copy_dirs(src, dst)

                # We store the source language ID to use it as a parameter in the retrieve_lid call during ocr
                # We store the client name to build paths more easily
                cache[project_folder] = (client, row[lid_col])

    return cache
