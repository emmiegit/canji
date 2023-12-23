from xml.etree import ElementTree

"""
Common functions and concepts used by multiple scripts
"""

XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'

DEFAULT_WIDTH = 109
DEFAULT_HEIGHT = 109
DEFAULT_VIEWBOX = f"0 0 {DEFAULT_WIDTH} {DEFAULT_HEIGHT}"


def parse_xml(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    return tree, root
