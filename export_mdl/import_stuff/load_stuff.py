from typing import BinaryIO

from export_mdl.import_stuff.MDXImportProperties import MDXImportProperties
from export_mdl.import_stuff.mdl_parser.parse_mdl import parse_mdl


def load_mdl(import_properties: MDXImportProperties):
    mdx_file = open(import_properties.mdx_file_path, 'r')
    mdx_file_data = mdx_file.read()
    mdx_file.close()
    parse_mdl(mdx_file_data, import_properties)
    print("Done!")


# this is for commandline testing
def load_mdl2():
    mdx_file = open('FILEPATH', 'r')
    mdx_file_data = mdx_file.read()
    mdx_file.close()
    # parse_mdl2(mdx_file_data)


def load_mdx(import_properties: MDXImportProperties):
    mdx_file: BinaryIO = open(import_properties.mdx_file_path, 'rb')
    mdx_file_data: bytes = mdx_file.read()
    mdx_file.close()
    # parse_mdx(mdx_file_data, import_properties)
    print("Done!")
