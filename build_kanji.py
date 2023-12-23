#!/usr/bin/env python3

import tomllib
from collections import namedtuple
from dataclasses import dataclass
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

from .common import DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_VIEWBOX, parse_xml


@dataclass
class SubImage:
    node: Element
    x: int
    y: int
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    viewbox: str = DEFAULT_VIEWBOX


def build_svg_from_parts(part):
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
        part.node.attrib = {
            "x": str(part.x),
            "y": str(part.y),
            "width": str(part.width),
            "height": str(part.height),
            "viewBox": part.viewbox,
        }

    return root


if __name__ == "__main__":
    raise NotImplementedError
