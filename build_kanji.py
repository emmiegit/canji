#!/usr/bin/env python3

"""
Generates randomly-created kanji.
Uses the radical positioning information in data.toml
and the extracted radical and character SVGs from extract_radicals.py
"""

import os
import random
import sys
import tomllib
from copy import deepcopy
from typing import Iterable
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from common import (
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    DEFAULT_VIEWBOX,
    parse_xml,
    register_xml_namespaces,
)
from data import Radical, ImagePart, read_data

XML_HEADER = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>'


def modify_stroke_thickness(element, stroke_multiplier):
    raise NotImplementedError


def build_svg(parts: Iterable[ImagePart]):
    root = Element(
        "svg",
        attrib={
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
            "preserveAspectRatio": "none",
        }
        if part.stroke_multiplier != 1:
            modify_stroke_thickness(element, part.stroke_multiplier)
        root.append(element)

    ElementTree.indent(root, space="\t", level=0)
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

    # Generate some random characters
    output_dir = os.path.expanduser("~/incoming")  # XXX
    for i in range(10):
        #radical = random.choice(data.radicals)
        radical = data.radical_names["street"]
        character = random.choice(data.characters)
        parts = radical.make_parts(character)
        svg = build_svg(parts)
        write_svg(os.path.join(output_dir, f"{i:02}.svg"), svg)
