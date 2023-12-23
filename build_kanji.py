#!/usr/bin/env python3

import os
import random
import sys
import tomllib
from copy import deepcopy
from typing import Iterable
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from common import DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_VIEWBOX, parse_xml
from data import Radical, ImagePart, read_data

XML_HEADER = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'


def build_svg(parts: Iterable[ImagePart]):
    root = Element(
        "svg",
        attrib={
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:kvg": "http://kanjivg.tagaini.net",
            "width": str(DEFAULT_WIDTH),
            "height": str(DEFAULT_HEIGHT),
            "viewBox": str(DEFAULT_VIEWBOX),
        },
    )

    for part in parts:
        element = deepcopy(part.node)
        element.attrib = {
            "x": str(part.x),
            "y": str(part.y),
            "width": str(part.width),
            "height": str(part.height),
            "viewBox": part.viewbox,
        }
        if part.character is not None:
            element.attrib["canji:element"] = part.character
        root.append(element)

    return root


def write_svg(path, root):
    with open(path, "wb") as file:
        file.write(XML_HEADER)
        file.write(b"\n")
        file.write(ElementTree.tostring(root, encoding="utf-8"))


if __name__ == "__main__":
    # TODO

    # Normalize current directory
    os.chdir(os.path.dirname(sys.argv[0]))

    # Setup
    register_xml_namespaces()
    data = read_data()

    # Generate one random character
    radical = random.choice(data.radicals)
    character = random.choice(data.characters)
    parts = radical.make_parts(character)
    svg = build_svg(parts)
    write_svg("_output.svg", svg)
