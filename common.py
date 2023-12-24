"""
Common functions and concepts used by multiple scripts
"""

from collections import namedtuple
from xml.etree import ElementTree

RADICAL_DIRECTORY = "radicals"
CHARACTER_DIRECTORY = "characters"

DEFAULT_WIDTH = 109
DEFAULT_HEIGHT = 109
DEFAULT_VIEWBOX = f"0 0 {DEFAULT_WIDTH} {DEFAULT_HEIGHT}"

XML_SVG_URL = "http://www.w3.org/2000/svg"
XML_KVG_URL = "http://kanjivg.tagaini.net"
XML_PREFIX_MAP = {
    "": XML_SVG_URL,
    "kvg": XML_KVG_URL,
}


def register_xml_namespaces():
    for key, value in XML_PREFIX_MAP.items():
        ElementTree.register_namespace(key, value)


def parse_xml(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    return tree, root
