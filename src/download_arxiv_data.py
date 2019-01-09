""" Script to download PDF and tex sources for a given PDF.
@author Jessica Tanon

JAN 2019
"""

import os
import requests
import sys
import wget
import tarfile
import logging
from os.path import exists, join
from arxiv_downloader_helper import get_download_folder

LOCAL_LATEX_SRC_PATH    = ""    # latex sources folder path
LOCAL_PDF_PATH          = ""    # pdf file path
DEST_PATH               = ""    # folder containing pdf and latex sources
ARCHIVE_NAME            = ""    # name of archive containing latex sources before extraction
logging.basicConfig(level=logging.INFO)


def arxiv_downloader_main(pdf_url):
    """ Creates needed folders and downloads data

    :param pdf_url: URL to pdf file on arxiv
    """

    if _is_valid_link(pdf_url):
        logging.info("PDF link: {}".format(pdf_url))
    else:
        sys.exit("Link to {} doesn't work, please check your link".format(pdf_url))

    _build_paths(pdf_url)
    _download_data(pdf_url)


def _build_paths(pdf_url):
    """ Creates paths to needed resources

    :param pdf_url: URL to PDF file
    """

    # Extracting names for folders to be created
    dl_folder_path      = get_download_folder()                         # Getting local Download folder
    pdf_name            = pdf_url.rsplit("/")[-1]                       # 1987.1234.pdf
    dest_folder_name    = pdf_name.rsplit(".", 1)[0].replace(".", "_")  # 1987_1234
    src_folder_path     = dest_folder_name + "_tex_src"                 # 1987_1234_tex_src

    # Setting global variables
    _set_dest_path(join(dl_folder_path, dest_folder_name))   # .../Downloads/1987_1234
    _set_src_path(src_folder_path)                           # .../Downloads/1987_1234/1987_1234_tex_src
    _set_pdf_path(pdf_name)                                  # .../Downloads/1987_1234/1987.1234.pdf
    _set_archive_name(pdf_name)                              # 1987.1234

    try:
        os.mkdir(DEST_PATH)
    except OSError as err:
        logging.error("Cannot create destination folder : {}".format(err))
        sys.exit(0)
    logging.info("SUCCESS --- Created destination folder at {}".format(DEST_PATH))

    # os.mkdir(LOCAL_LATEX_SRC_PATH)
    # logging.info("SUCCESS --- Created latex source folder at {}".format(LOCAL_LATEX_SRC_PATH))


def _set_dest_path(dest_path):
    """ Sets main destination folder path """
    global DEST_PATH
    DEST_PATH = dest_path


def _set_pdf_path(pdf_name):
    """ Sets PDF file path """
    global LOCAL_PDF_PATH
    LOCAL_PDF_PATH = join(DEST_PATH, pdf_name)


def _set_src_path(tex_src_name):
    """ Sets latex sources folder path """
    global LOCAL_LATEX_SRC_PATH
    LOCAL_LATEX_SRC_PATH = join(DEST_PATH, tex_src_name)


def _set_archive_name(pdf_name):
    """ Sets archive file name """
    global ARCHIVE_NAME
    ARCHIVE_NAME = pdf_name.rsplit(".", 1)[0]


def get_dest_path():
    """ Returns destination folder absolute path """
    return DEST_PATH


def get_pdf_path():
    """ Returns the PDF abs path """
    return LOCAL_PDF_PATH


def get_latex_src_path():
    return LOCAL_LATEX_SRC_PATH


def _is_valid_link(link, check_src=False):
    """ Checks if the URL provided to the PDF file is valid

    :param link: link to the PDF file, e.g. `https://arxiv.org/pdf/1812.11928.pdf` """
    logging.info("Checking link validity...")
    request = requests.get(link)
    if request.status_code == 200:
        if check_src:
            headers = request.headers
            # Seems to indicate an attempt to download non-existent sources redirected to the PDF
            if headers['Content-Type'] == 'application/pdf' and headers['Content-Encoding'] == 'gzip':
                return False
        return True
    return False


def _build_tex_source_link_name(pdf_dl_link):
    """ Builds tex source folder download link from the pdf link

    :param pdf_dl_link: pdf download link
    :return: tex src folder download link
    """
    base = "https://arxiv.org/e-print/"
    pdf_no_ext = pdf_dl_link.rsplit("/")[-1].rsplit(".", 1)[0]
    return base + pdf_no_ext


def _download_pdf(pdf_url):
    if exists(LOCAL_PDF_PATH):
        logging.info("PDF file already exists, won't download again")
    else:
        try:
            wget.download(pdf_url, out=DEST_PATH)
        except Exception as e:
            logging.error("Cannot download PDF file : {}".format(e))
            sys.exit(0)


def _download_latex_sources(latex_src_url):

    if exists(join(LOCAL_LATEX_SRC_PATH, ARCHIVE_NAME)):
        logging.info("Latex sources already exist, won't download again")
    else:
        if _is_valid_link(latex_src_url, check_src=True):
            os.mkdir(LOCAL_LATEX_SRC_PATH)
            logging.info("SUCCESS --- Created latex source folder at {}".format(LOCAL_LATEX_SRC_PATH))
            try:
                wget.download(latex_src_url, out=LOCAL_LATEX_SRC_PATH)
            except Exception as e:
                logging.error("Download failed: {}".format(e))
        else:
            _set_src_path("") # Emptying sources path
            logging.info("There are no sources available for this PDF file.")


def _download_data(pdf_url):
    _download_pdf(pdf_url)
    latex_src_url = _build_tex_source_link_name(pdf_url)
    _download_latex_sources(latex_src_url)
    print("SRC: ", LOCAL_LATEX_SRC_PATH)
    if LOCAL_LATEX_SRC_PATH != "":
        _extract_src()


def _extract_src():
    """ Extract downloaded tex src archive

    :param archive_name: name of archive file
    :param dest_path: destination folder
    """
    logging.info("Extracting {}...".format(ARCHIVE_NAME))
    tar = tarfile.open(join(LOCAL_LATEX_SRC_PATH, ARCHIVE_NAME))
    tar.extractall(path=join(LOCAL_LATEX_SRC_PATH))
    logging.info("Removing archive file...")
    os.remove(join(LOCAL_LATEX_SRC_PATH, ARCHIVE_NAME))
    tar.close()


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description="Downloader for arxiv PDF and latex source files")
    parser.add_argument("pdf_url", type=str, help="Link to PRD arxiv file")
    args = parser.parse_args()
    arxiv_downloader_main(**(vars(args)))
