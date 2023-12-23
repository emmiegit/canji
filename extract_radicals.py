#!/usr/bin/env python3

import os
import re
import sys
import unicodedata
from xml.etree import ElementTree

from .common import parse_xml

KANJIVG_DIRECTORY = "kanjivg/kanji"
OUTPUT_DIRECTORY = "radicals"

REGULAR_KANJI_PATH_REGEX = re.compile(r"(\w+)\.svg")


def process_kanji(root):
    # Delete stroke order
    assert "StrokeNumbers" in root[1].get("id", "")
    del root[1]


if __name__ == "__main__":
    # Normalize current directory
    os.chdir(os.path.dirname(sys.argv[0]))

    # Create output directory
    if not os.path.isdir(OUTPUT_DIRECTORY):
        os.mkdir(OUTPUT_DIRECTORY)

    # Register namespace
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
    ElementTree.register_namespace("kvg", "http://kanjivg.tagaini.net")

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
        output_path = os.path.join(OUTPUT_DIRECTORY, path)

        tree, root = parse_xml(input_path)
        process_kanji(root)
        tree.write(output_path, encoding="utf-8")
