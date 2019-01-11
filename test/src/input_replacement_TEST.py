""" Script to test multiple inputs replacements
@author Jessica Tanon

JAN 2019
"""

import unittest
from os.path import join, exists
from shutil import rmtree
from arxiv_downloader_helper import get_download_folder
import parse_latex as pl
import logging
from os import listdir
import re

logging.basicConfig(level="INFO")

EXP1 = open("../resources/multiple_inputs_ex1_expected.tex").read()


class TestMultipleInputs(unittest.TestCase):

    def test_this(self):
        self.maxDiff = None
        replaced = pl.parser_main("../resources/1901", ret=True)
        self.assertEqual(EXP1, replaced)
