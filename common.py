from collections import namedtuple
from xml.etree import ElementTree

"""
Common functions and concepts used by multiple scripts
"""

RADICAL_DIRECTORY = "radicals"
CHARACTER_DIRECTORY = "characters"

DEFAULT_WIDTH = 109
DEFAULT_HEIGHT = 109
DEFAULT_VIEWBOX = f"0 0 {DEFAULT_WIDTH} {DEFAULT_HEIGHT}"


def register_xml_namespaces():
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
    ElementTree.register_namespace("kvg", "http://kanjivg.tagaini.net")


def parse_xml(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    return tree, root
