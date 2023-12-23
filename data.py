import os
import tomllib
from dataclasses import dataclass
from typing import Optional, Union
from xml.etree.ElementTree import Element

from common import RADICAL_DIRECTORY, CHARACTER_DIRECTORY, DEFAULT_VIEWBOX, parse_xml

"""
Code to read the data file for kanji processing.
"""


@dataclass
class ImagePart:
    character: Optional[str]
    node: Element
    x: int
    y: int
    width: int
    height: int
    viewbox: str = DEFAULT_VIEWBOX


@dataclass
class Radical:
    character: Optional[str]
    file: str
    position: Union[0, 1]
    node: Element
    x: tuple[int, int]
    y: tuple[int, int]
    width: tuple[int, int]
    height: tuple[int, int]
    viewbox: str

    def make_parts(self, other: Element):
        parts = []
        for pos in (0, 1):
            this = self.position == pos
            parts.append(
                ImagePart(
                    x=self.x[pos],
                    y=self.y[pos],
                    width=self.width[pos],
                    height=self.height[pos],
                    node=self.node if this else other,
                    viewbox=self.viewbox if this else DEFAULT_VIEWBOX,
                )
            )
        return parts


@dataclass
class KanjiData:
    radical_list: frozenset[str]
    radicals: list[Radical]

    def is_radical(self, s: str) -> bool:
        return s in self.radical_list


def read_data(path="data.toml", load_radicals=True):
    with open(path, "rb") as file:
        data = tomllib.load(file)

    radical_list = set()

    def make(entry):
        char = entry.get("char")
        if char is not None:
            radical_list.add(char)

        file = entry.get("file")
        if file is None:
            assert char is not None, "One of char, file must be specified!"
            file = f"{ord(char):05x}.svg"

        if load_radicals:
            node = parse_xml(os.path.join(RADICAL_DIRECTORY, file))
        else:
            node = Element("null")

        return Radical(
            character=char,
            file=file,
            position=entry["pos"],
            x=entry["x"],
            y=entry["y"],
            width=entry["width"],
            height=entry["height"],
            viewbox=entry["viewbox"],
            node=node,
        )

    radicals = list(map(make, data["radicals"]))
    return KanjiData(radicals=radicals, radical_list=frozenset(radical_list))
