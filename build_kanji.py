#!/usr/bin/env python3

"""
Generates randomly-created kanji.
Uses the radical positioning information in data.toml
and the extracted radical and character SVGs from extract_radicals.py
"""

import argparse
import math
import os
import random
import sys
import tomllib
from copy import deepcopy
from typing import Iterable
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

try:
    from alive_progress import alive_bar
except ImportError:
    from dummy_bar import DummyBar as alive_bar

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
from dummy_bar import DummyBar


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
        root.attrib["kvg:element"] = "".join(p.character for p in parts if p.character)

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


def generate(radicals, characters):
    radical = random.choice(radicals)
    character = random.choice(characters)
    parts = radical.make_parts(character)
    return build_svg_from_parts(parts)


if __name__ == "__main__":
    # Process command-line arguments
    argparser = argparse.ArgumentParser(description="Procedurally generate kanji")
    argparser.add_argument(
        "-c",
        "--count",
        dest="count",
        type=int,
        default=10,
        help="The number of kanji to generate",
    )
    argparser.add_argument(
        "-o",
        "--output",
        dest="output",
        default=".",
        help="The directory to write generated kanji into. If only one character is being generated, this is treated as a target path instead.",
    )
    argparser.add_argument(
        "-d",
        "--data",
        dest="data_file",
        default="data.toml",
        help="The data file to use in generation. Path is relative to the location of this script.",
    )
    argparser.add_argument(
        "-r",
        "--radical",
        dest="radicals",
        nargs="*",
        help="List of radicals (by data file name) to use in generation. Default is randomly choose among all.",
    )
    argparser.add_argument(
        "-C",
        "--char",
        "--character",
        dest="characters",
        nargs="*",
        help="List of characters (by character value or filename) to use in generation. Default is randomly choose among all.",
    )
    argparser.add_argument(
        "-p",
        "--progress",
        "--fancy-progress",
        dest="fancy_progress",
        action="store_true",
        help="Use the fancy progress bar. Requires alive_progress dependency to be installed.",
    )
    args = argparser.parse_args()
    make_bar = alive_bar if args.fancy_progress else DummyBar
    output = os.path.abspath(args.output)

    # Normalize current directory
    os.chdir(os.path.dirname(sys.argv[0]))

    # Setup
    register_xml_namespaces()
    data = read_data(args.data_file)

    radicals = (
        [data.radical_names[n] for n in args.radicals]
        if args.radicals
        else data.radicals
    )
    characters = (
        [data.character_by_id(n) for n in args.characters]
        if args.characters
        else data.characters
    )

    # Special handling for single-character generation
    if args.count == 1:
        svg = generate(radicals, characters)
        write_svg(output, svg)
        sys.exit(0)

    # Generate some random characters
    idx_width = math.ceil(math.log10(args.count + 1))
    with make_bar(args.count) as bar:
        for i in range(args.count):
            svg = generate(radicals, characters)
            idx = str(i).zfill(idx_width)
            write_svg(os.path.join(output, f"{idx}.svg"), svg)
            bar()
