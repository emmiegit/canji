"""
Common functions and concepts used by multiple scripts
"""

from collections import namedtuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

RADICAL_DIRECTORY = "radicals"
CHARACTER_DIRECTORY = "characters"

DEFAULT_WIDTH = 109
DEFAULT_HEIGHT = 109
DEFAULT_VIEWBOX = f"0 0 {DEFAULT_WIDTH} {DEFAULT_HEIGHT}"

XML_HEADER = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
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


def build_svg(inner, *, add_style) -> Element:
    root = Element(
        "svg",
        attrib={
            "width": str(DEFAULT_WIDTH),
            "height": str(DEFAULT_HEIGHT),
            "viewBox": DEFAULT_VIEWBOX,
        },
    )

    if add_style:
        wrap = Element(
            "g",
            attrib={
                "style": "fill:none;stroke:#000000;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;"
            },
        )
        root.append(wrap)
        inner(wrap)
    else:
        inner(root)

    ElementTree.indent(root, space="\t", level=0)
    return root


def write_svg(path, root):
    with open(path, "wb") as file:
        file.write(XML_HEADER)
        file.write(b"\n")
        file.write(ElementTree.tostring(root, encoding="utf-8"))
