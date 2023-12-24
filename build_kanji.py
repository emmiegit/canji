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
    build_svg,
    parse_xml,
    write_svg,
    register_xml_namespaces,
)
from data import Radical, ImagePart, read_data


def modify_stroke_thickness(element, stroke_multiplier):
    group = element[0]
    assert "kvg:StrokePaths" in group.attrib["id"]
    assert "style" in group.attrib

    # Rebuild inline CSS with multiplied stroke-width value.
    style_parts = group.attrib["style"].split(";")
    for i, style_part in enumerate(style_parts):
        if not style_part:
            continue

        key, value = style_part.split(":")
        if key != "stroke-width":
            continue

        new_value = float(value) * stroke_multiplier
        style_parts[i] = f"stroke-width:{new_value}"

    # Replace with rebuilt inline CSS
    group.attrib["style"] = ";".join(style_parts)


def build_svg_from_parts(parts: Iterable[ImagePart]):
    def inner(root):
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

    return build_svg(inner, add_style=False)


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
        # radical = random.choice(data.radicals)
        radical = data.radical_names["saber"]
        character = random.choice(data.characters)
        parts = radical.make_parts(character)
        svg = build_svg_from_parts(parts)
        write_svg(os.path.join(output_dir, f"{i:02}.svg"), svg)
