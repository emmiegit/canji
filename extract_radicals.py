#!/usr/bin/env python3

"""
Extracts character and radical SVGs from KanjiVG SVG files.
Essentially the pre-processing step required for this project.
"""

import os
import re
import sys
import unicodedata
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from alive_progress import alive_bar

from charid import hex_to_char
from common import (
    RADICAL_DIRECTORY,
    CHARACTER_DIRECTORY,
    DEFAULT_VIEWBOX,
    XML_KVG_URL,
    XML_SVG_URL,
    build_svg,
    parse_xml,
    register_xml_namespaces,
    write_svg,
)
from data import read_data

KANJIVG_DIRECTORY = "kanjivg/kanji"
REGULAR_KANJI_PATH_REGEX = re.compile(r"(\w+)\.svg")


def find_element(root, element):
    svg_prefix = f"{{{XML_SVG_URL}}}"
    kvg_prefix = f"{{{XML_KVG_URL}}}"
    if (
        root.tag == f"{svg_prefix}g"
        and root.attrib.get(f"{kvg_prefix}element") == element
    ):
        return root

    for child in root:
        result = find_element(child, element)
        if result is not None:
            return result

    return None


def make_svg_from_extraction(root, element_str):
    extracted = find_element(root, element_str)
    assert extracted, "Could not find element to extract"
    output_path = os.path.join(RADICAL_DIRECTORY, extraction.output)
    svg = build_svg(lambda root: root.append(extracted), add_style=True)
    write_svg(output_path, svg)


def process_kanji(root):
    # Delete stroke order
    assert "StrokeNumbers" in root[1].get("id", "")
    del root[1]


if __name__ == "__main__":
    # Normalize current directory
    os.chdir(os.path.dirname(sys.argv[0]))

    # Create output directory
    os.makedirs(RADICAL_DIRECTORY, exist_ok=True)
    os.makedirs(CHARACTER_DIRECTORY, exist_ok=True)

    # Setup
    register_xml_namespaces()
    data = read_data()

    def is_radical(file):
        return any(map(lambda r: os.path.basename(r.path) == file and r.copy, data.radicals))

    # Process KanjiVG files
    print("Processing KanjiVG files...")
    kanjivg_paths = os.listdir(KANJIVG_DIRECTORY)
    with alive_bar(len(kanjivg_paths) + data.extractions_count()) as bar:
        for path in kanjivg_paths:
            # Skip, only consider non-variants
            match = REGULAR_KANJI_PATH_REGEX.fullmatch(path)
            if match is None:
                bar(skipped=True)
                continue

            # Skip, based on categorization of character
            char = hex_to_char(match[1])
            char_name = unicodedata.name(char)
            if "CJK" not in char_name:
                bar(skipped=True)
                continue

            # Skip, excluded
            if char in data.characters_exclude:
                bar(skipped=True)
                continue

            # Pre-process character/radical, moving to appropriate destination
            input_path = os.path.join(KANJIVG_DIRECTORY, path)
            output_path = os.path.join(
                RADICAL_DIRECTORY if is_radical(path) else CHARACTER_DIRECTORY,
                path,
            )

            tree, root = parse_xml(input_path)
            process_kanji(root)
            tree.write(output_path, encoding="utf-8")
            bar()

            # If we have any extractions from this character, then do those
            for extraction in data.extractions[path]:
                make_svg_from_extraction(root, extraction.element)
                bar()
