import os
import logging

from sources.config import PATH_TO_PG, PATH_TO_PGA, TOP_DIR, BASE_DIR, PATH_TO_FR, FILE_SIZE_FILTER, lid_dict


def flat_convert():
    """Convert working files to .TXT format.

    This function runs a preconfigured PowerGrep5 action to convert writable files in the working folder.
    The action excludes PDF files.
    """
    path_to_results = os.path.join(TOP_DIR, "results.html")
    path_to_action = os.path.join(BASE_DIR, PATH_TO_PGA)

    command = "PowerGrep5.exe /folderrecurse \"" + \
              TOP_DIR + "\" \"" + \
              path_to_action + "\" /silent /save \"" + \
              path_to_results + "\" /quit"

    os.chdir(PATH_TO_PG)
    os.system(command)
    logging.info("Results written to: {}".format(path_to_results))

    os.chdir(BASE_DIR)


def find_failed_conversions():
    """Search for files where conversion has likely failed."""
    fails = []

    for root, dirs, files in os.walk(TOP_DIR):

        for file in filter(lambda file: file.lower().endswith('pdf.txt'), files):
            if os.path.getsize(os.path.join(root, file)) < FILE_SIZE_FILTER:
                fails.append(os.path.join(root, file))
                # yield(os.path.join(root, file))
    return fails


def run_ocr(fp, cache):
    """Run OCR tool on documents that were presumably scanned.

    Arguments:
        fp -- Path to *.txt file flagged because file size < FILE_SIZE_FILTER
        cache -- Dictionary mapping project folder names to client names and source language IDs
    """
    lang = retrieve_lid(fp, cache)
    # Remove ".txt" extension from file path
    path_to_file = fp[:-4]

    command = "FineCmd.exe \"" + \
               path_to_file + "\"" + \
               " /lang " + lang + \
               " /out \"" + fp + "\" /quit"

    os.chdir(PATH_TO_FR)
    os.system(command)

    logging.info("OCR results written to: {}".format(fp))
    os.chdir(BASE_DIR)


def terminate_finereader():
    """Terminate all FineReader processes.

    Note:
        This command should kill the FineReader parent process and all child processes.
        Note that there sometimes is an error which prevents taskkill from executing.
        In this case, you will need to run the following command manually for each batch.
    """
    command = "taskkill /F /IM FineReader.exe /T"
    os.system(command)


def retrieve_lid(fp, cache):
    """Parse language ID from path to file.

    Arguments:
        fp -- Path to *.txt file flagged because file size < FILE_SIZE_FILTER
        cache -- Dictionary mapping project folder names to client names and source language IDs
    """
    # tail = fp[len(TOP_DIR) + 1:]
    head = os.path.dirname(fp)
    project_folder = os.path.basename(head)
    lid = cache.get(project_folder, None)[-1]

    # See "ABBYY FineReader 11/FinereaderCmd.txt" for valid language names
    # Will default to "english french german italian" if integer is "00", None or other

    return lid_dict.get(lid, "english french german italian")
