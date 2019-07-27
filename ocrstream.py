
import os
import logging
from time import sleep
from multiprocessing.pool import Pool

from sources.transform import find_failed_conversions, flat_convert, run_ocr, terminate_finereader
from sources.extract import copy_source_files
from sources.load import load_to_corpus


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

TW_EXPORT = "20190726\\order_out_AMS2.csv"
PRJ_DIR = "H:\\02_working\\05projects\\07OCRstream\\02Dev\\ocrstream\\data"

path_to_action = "H:\\02_working\\05projects\\07OCRstream\\01Prototype\\flat_conversion_to_txt_(all_formats).pga"
source_root = 'F:\\Kundenaufträge ab Dez 2010'

clients = {"11385": "Parexel BERLIN 11385",
           "21611": "medpace 21611",
           "21650": "CTI Clinical Trial and Consulting Services Europe GmbH 21650",
           "26422": "AMS Advanced Medical Services GmbH 26422",
           "30553": "AMS UK 30553",
           "98036": "AMS Advanced Medical Services GmbH 98036"
           }


class MyPipeline(object):

    def __init__(self):
        self.fp = os.path.join(PRJ_DIR, TW_EXPORT)
        self.TIMEOUT = 60
        self.SLEEP = 10
        self.BATCH_SIZE = 50
        self.client_dict = clients
        self.cache = dict()

    def copy_files(self):
        """
        Copy project source files listed in TW export to target directory (TOP DIR)

        Arguments:
             fp -- path to TW CSV export with the following columns:
                    addressID, auftragsDatum, projektNR, D160_prt_D161_AUFTRAG_POS__::_kc_spp_ID

        """

        self.cache = copy_source_files(self.fp, self.client_dict, source_root)

    @staticmethod
    def convert():
        flat_convert(path_to_action)

    def ocr(self):

        fails = find_failed_conversions()

        def batch(my_list, n=1):
            length = len(my_list)
            for ndx in range(0, length, n):
                yield my_list[ndx:min(ndx + n, length)]

        # Li
        for x in batch(fails, self.BATCH_SIZE):
            self.batch_workers(x)

        logging.info("No. of empty files: {}.".format(len(find_failed_conversions())))

    def batch_workers(self, fails):

        pool = Pool(processes=len(fails))

        # Spawn a new worker for each doc that requires OCR processing
        # The number of concurrently running workers is determined by the number of CPU cores
        for i in range(len(fails)):
            pool.apply_async(run_ocr, args=(fails[i], self.cache))
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

    def load(self):
        load_to_corpus(self.cache)


if __name__ == '__main__':
    p = MyPipeline()
    p.copy_files()
    p.convert()
    p.ocr()
    p.load()


