
import os
import logging
from time import sleep
from multiprocessing.pool import Pool

from sources.transform import find_failed_conversions, flat_convert, run_ocr, terminate_finereader
from sources.extract import copy_source_files
from sources.load import load_to_corpus


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

TW_EXPORT = "20190720\\order_out.csv"
PRJ_DIR = "H:\\02_working\\05projects\\07OCRstream\\01Prototype\\data"

path_to_action = "H:\\02_working\\05projects\\07OCRstream\\01Prototype\\flat_conversion_to_txt_(all_formats).pga"
source_root = 'F:\\Kundenaufträge ab Dez 2010\\Parexel BERLIN 11385\\03_Projekte'


class MyPipeline(object):

    def __init__(self):
        self.fp = os.path.join(PRJ_DIR, TW_EXPORT)
        self.TIMEOUT = 60
        self.SLEEP = 10

    def copy_files(self):
        copy_source_files(self.fp, source_root)

    @staticmethod
    def convert():
        flat_convert(path_to_action)

    def ocr(self):

        fails = find_failed_conversions()

        number_of_workers = len(fails)

        pool = Pool(processes=number_of_workers)

        # Spawn a new worker for each doc that requires OCR processing
        # The number of concurrently running workers is determined by the number of CPU cores
        for i in range(number_of_workers):
            pool.apply_async(run_ocr, args=(fails[i], ))
            # Add sleep time to prevent licensing errors messages
            sleep(self.SLEEP)

        pool.close()
        print("Waiting for FineReader to finish…", end='')

        cnt = 0
        while len(find_failed_conversions()) > 0 and cnt < self.TIMEOUT:
            print(".", end='')
            sleep(self.SLEEP)
            cnt += self.SLEEP

        terminate_finereader()
        pool.join()
        logging.info("All processes joined")
        logging.info("No. of empty files: {}.".format(len(find_failed_conversions())))

    @staticmethod
    def load():
        load_to_corpus()


if __name__ == '__main__':
    p = MyPipeline()
    p.copy_files()
    p.convert()
    p.ocr()
    p.load()


