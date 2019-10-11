import os
from collections import Counter, defaultdict

import pandas as pd

from sources.utils import copy_files, delete_dir
from sources.config import TOP_DIR, CORPUS_TEMP, DATABASE_EXPORTS_FOLDER


def load_to_corpus(cache):
    """Copy OCRed .TXT files to staging directory.

    Arguments:
        cache -- Dictionary mapping project folder names to client names and source language IDs
    """
    delete_dir(CORPUS_TEMP)

    for root, dirs, files in os.walk(TOP_DIR):
        for file in filter(lambda file: file.lower().endswith('.txt'), files):

            src = os.path.join(root, file)
            # Extract project folder name from path
            project_folder = os.path.basename(root)
            # Lookup client name in cache
            client_folder = cache.get(project_folder, 'Fail')[0]
            # Build path from client name and project folder name
            dst = os.path.join(CORPUS_TEMP, os.path.join(client_folder, project_folder))

            copy_files(src, dst)


def get_most_recent_folder():
    """Get most recent folder in data folder."""
    root = DATABASE_EXPORTS_FOLDER
    all_subdirs = [os.path.join(root, d) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
    # Fetch the folder that has been modified most recently
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    return latest_subdir


def get_most_recent_export(subdir):
    """Get most recent data export.

    Arguments:
        subdir -- path to most recently modified folder
    Returns:

        file -- path to data export to be cleaned.

    Raises:
         Exception -- If a file of the name "order_out.csv" already exists.
    """
    for file in filter(lambda file: file.lower().endswith(('.csv', '.xlsx')), os.listdir(subdir)):
        if file == "order_out.csv":
            raise Exception(f'Process skipped. {file} already exists!')

    return file


def load_data(fp):
    """Read CSV data from ERP export.

    Arguments:
        fp -- path/to/file as string.

    The export data is expected to include the following column data:
    Address ID: Mapping to client folder names as per the client_dict configuration variable
    Project No: Referencing project folder names
    Language pair: Mapping to language string variables as per the lid_dict configuration variable

    Returns:
        df -- table with pre-processed export data

    Raises:
        ValueError -- if file path does not exist
    """
    try:
        df = pd.read_excel(fp, na_values='eco',  # Unsure why "eco" is in the spp column, only numerics are allowed
                           dtype={"adressID": str,
                                  "auftragsDatum": str,
                                  "projektNr": str,
                                  "D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID": str}
                           )
        df.dropna(subset=["D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID"], inplace=True)
        # Fill empty cells with previous column values
        df.fillna(method='ffill', inplace=True)

    except ValueError:
        print(f'{fp}')

    return df


def count_spps(df):
    """Get most probable source language per project.

    Arguments:
        df -- table with pre-processed export data
    Returns:
        prj_to_spp -- dictionary with language IDs as values and project IDs as keys
    """
    prj_to_spp = defaultdict(str)

    # Iterate over unique project ids
    for prj in df['projektNr'].unique():
        # Extract source language id from strings in spp column.
        spps = df[df['projektNr'] == prj]['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'].str[0:2].values
        # Iterate over list of strings and count occurrences
        cnt = Counter(spps)
        # If source language id includes '00', set count to zero
        if cnt.get('00', False):
            cnt['00'] = 0

        # Map most common source language to project ID
        prj_to_spp[prj] = cnt.most_common(1)[0][0]
    return prj_to_spp


def clean_data(df, prj_to_spp):
    """Clean language IDs and duplicate data.

    Arguments:
        df -- table with pre-processed export data
        prj_to_spp -- dictionary with language IDs as values and project IDs as keys
    Returns:
        df -- table with clean export data
    """
    # Replace SPP column with project ID column
    df['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'] = df['projektNr']
    # Look up project ID in dictionary and replace table value with dictionary value
    df['D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID'].replace(to_replace=prj_to_spp, inplace=True)
    # Remove rows with duplicate project IDs and return table
    df.drop_duplicates(subset="projektNr", inplace=True)
    return df


def parse_order_data():
    """Pre-process nested order data from ERP export.

    Returns:
        dst -- path/to/file with clean export data
    """
    directory = get_most_recent_folder()

    try:
        src = get_most_recent_export(directory)
    except Exception:
        return os.path.join(directory, "order_out.csv")

    df = load_data(os.path.join(directory, src))
    print('Loading from {}'.format(os.path.join(directory, src)))

    prj_to_spp = count_spps(df)
    df = clean_data(df, prj_to_spp)
    dst = os.path.join(directory, "order_out.csv")
    df.to_csv(dst, sep=',')
    print(f'Saved to {dst}')
    return dst
