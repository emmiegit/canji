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

from common import RADICAL_DIRECTORY, CHARACTER_DIRECTORY, parse_xml, register_xml_namespaces
from data import read_data

KANJIVG_DIRECTORY = "kanjivg/kanji"
REGULAR_KANJI_PATH_REGEX = re.compile(r"(\w+)\.svg")


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
        return any(map(lambda r: os.path.basename(r.path) == file, data.radicals))

    # Process KanjiVG files
    for path in os.listdir(KANJIVG_DIRECTORY):
        # Skip, only consider non-variants
        match = REGULAR_KANJI_PATH_REGEX.fullmatch(path)
        if match is None:
            continue

        # Skip, based on categorization of character
        char = chr(int(match[1], 16))
        char_name = unicodedata.name(char)
        if "CJK" not in char_name:
            continue

        input_path = os.path.join(KANJIVG_DIRECTORY, path)
        output_path = os.path.join(
            RADICAL_DIRECTORY if is_radical(path) else CHARACTER_DIRECTORY,
            path,
        )

        tree, root = parse_xml(input_path)
        process_kanji(root)
        tree.write(output_path, encoding="utf-8")
