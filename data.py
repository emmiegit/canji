"""
Code to read the data file for kanji processing.
"""

import os
import re
import tomllib
from dataclasses import dataclass
from typing import Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from common import RADICAL_DIRECTORY, CHARACTER_DIRECTORY, DEFAULT_VIEWBOX, parse_xml

SVG_FILENAME_REGEX = re.compile(r"([0-9a-f]+)\.svg")


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
class Character:
    character: Optional[str]
    path: str
    _tree: Optional[ElementTree] = None
    _node: Optional[Element] = None

    @property
    def node(self) -> Element:
        if self._node is None:
            self._tree, self._node = parse_xml(self.path)

        return self._node


@dataclass
class Radical:
    name: Optional[str]
    character: Optional[str]
    path: str
    position: Union[0, 1]
    x: tuple[int, int]
    y: tuple[int, int]
    width: tuple[int, int]
    height: tuple[int, int]
    viewbox: str
    _tree: Optional[ElementTree] = None
    _node: Optional[Element] = None

    @property
    def node(self) -> Element:
        if self._node is None:
            self._tree, self._node = parse_xml(self.path)

        return self._node

    def make_parts(self, other: Character) -> list[ImagePart]:
        parts = []
        for pos in (0, 1):
            this = self.position == pos
            parts.append(
                ImagePart(
                    x=self.x[pos],
                    y=self.y[pos],
                    width=self.width[pos],
                    height=self.height[pos],
                    character=self.character if this else other.character,
                    node=self.node if this else other.node,
                    viewbox=self.viewbox if this else DEFAULT_VIEWBOX,
                )
            )
        return parts


@dataclass
class KanjiData:
    radical_set: frozenset[str]
    radical_names: dict[str, Radical]
    radicals: list[Radical]
    characters: list[Character]

    def is_radical(self, s: str) -> bool:
        return s in self.radical_set


def read_data(path="data.toml"):
    with open(path, "rb") as file:
        data = tomllib.load(file)

    radical_set = set()
    radical_names = {}

    def make_radical(entry):
        char = entry.get("char")
        if char is not None:
            radical_set.add(char)

        file = entry.get("file")
        if file is None:
            assert char is not None, "One of char, file must be specified!"
            file = f"{ord(char):05x}.svg"

        radical = Radical(
            character=char,
            path=os.path.join(RADICAL_DIRECTORY, file),
            position=entry["pos"],
            x=entry["x"],
            y=entry["y"],
            width=entry["width"],
            height=entry["height"],
            viewbox=entry["viewbox"],
        )

        name = entry.get("name")
        if name is not None:
            assert name not in radical_names, f"Radical name {name} is not unique!"
            radical_names[name] = radical

        return radical

    def make_character(file):
        match = SVG_FILENAME_REGEX.fullmatch(file)
        if match is None:
            character = None
        else:
            character = chr(int(match[1], 16))

        path = os.path.join(CHARACTER_DIRECTORY, file)
        return Character(
            character=character,
            path=path,
        )

    radicals = list(map(make_radical, data["radicals"]))
    characters = list(map(make_character, os.listdir(CHARACTER_DIRECTORY)))

    return KanjiData(
        radicals=radicals,
        radical_set=frozenset(radical_set),
        radical_names=radical_names,
        characters=characters,
    )
