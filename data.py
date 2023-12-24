"""
Code to read the data file for kanji processing.
"""

import os
import re
import tomllib
from collections import defaultdict
from copy import copy
from dataclasses import dataclass
from typing import Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from common import (
    RADICAL_DIRECTORY,
    CHARACTER_DIRECTORY,
    DEFAULT_VIEWBOX,
    XML_KVG_PREFIX,
    parse_xml,
)
from charid import char_to_file

SVG_FILENAME_REGEX = re.compile(r"([0-9a-f]+)\.svg")


@dataclass
class Extraction:
    name: str
    input: str
    output: str
    element: str


@dataclass
class ImagePart:
    character: Optional[str]
    node: Element
    x: int
    y: int
    width: int
    height: int
    stroke_multiplier: float
    apply_weighting: bool
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
    copy: bool
    position: Union[0, 1]
    x: tuple[int, int]
    y: tuple[int, int]
    width: tuple[int, int]
    height: tuple[int, int]
    stroke_multiplier: tuple[float, float]
    apply_weighting: bool
    viewbox: str
    _tree: Optional[ElementTree] = None
    _node: Optional[Element] = None

    @property
    def node(self) -> Element:
        if self._node is None:
            self._tree, self._node = parse_xml(self.path)

        return self._node

    def make_parts(self, other: Character) -> list[ImagePart]:
        x = copy(self.x)
        y = copy(self.y)
        width = copy(self.width)
        height = copy(self.height)

        if self.apply_weighting:
            # Determine character weight, see if we need to squash even more
            #
            # This uses a heurestic which essentially says, hey, more complicated
            # radicals tend to use more room, and simple ones get squashed when
            # they appear next to a complicated one. But if they're both simple
            # or both complicated they get more or less equal amounts of space.
            #
            # So this basically fudges with the proportions a bit depending on the
            # "weight" of each character. If it has more sub-radicals, then we
            # treat it as more "complicated", and thus it gets more leeway
            #
            # As part of the modification, if both fields are the same
            # (e.g. they both have a starting X position of 0), then we assume
            # that this radical doesn't stretch in that direction, so we should
            # apply no fudging to it.

            diff = weight(self.node) - weight(other.node)
            diff *= 1 if self.position == 0 else -1

            def adjust(vals, modifier):
                if vals[0] != vals[1]:
                    vals[0] += diff * modifier
                    vals[1] -= diff * modifier

            adjust(x, -0.2)
            adjust(y, -0.2)
            adjust(width, 0.3)
            adjust(height, 0.3)

        # Build image parts for construction
        parts = []
        for pos in (0, 1):
            this = self.position == pos
            parts.append(
                ImagePart(
                    x=x[pos],
                    y=y[pos],
                    width=width[pos],
                    height=height[pos],
                    stroke_multiplier=self.stroke_multiplier[pos],
                    apply_weighting=self.apply_weighting,
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
    characters_exclude: frozenset[str]
    extractions: dict[str, Extraction]

    def is_radical(self, s: str) -> bool:
        return s in self.radical_set

    def extractions_count(self) -> int:
        return sum(len(v) for v in self.extractions.values())

    def character_by_id(self, id) -> Character:
        if len(id) == 1:
            # Assuming to be character
            condition = lambda c: c.character == id
        else:
            # Assuming to be path
            condition = lambda c: c.path == id

        for character in self.characters:
            if condition(character):
                return character

        raise ValueError(f"No character found with ID {id}")


def weight(node):
    this_weight = int(f"{XML_KVG_PREFIX}element" in node.attrib)
    children_weight = sum(map(weight, node))
    return this_weight + children_weight


def read_data(path="data.toml"):
    with open(path, "rb") as file:
        data = tomllib.load(file)

    radical_set = set()
    radical_names = {}

    def make_radical(entry):
        char = entry.get("char")
        name = entry.get("name")
        file = entry.get("file")

        if file is None:
            assert char is not None, "One of char, file must be specified!"
            file = char_to_file(char)

        radical = Radical(
            name=name,
            character=char,
            path=os.path.join(RADICAL_DIRECTORY, file),
            copy=entry.get("copy", True),
            position=entry["pos"],
            x=entry.get("x", (0, 0)),
            y=entry.get("y", (0, 0)),
            width=entry.get("width", (109, 109)),
            height=entry.get("height", (109, 109)),
            stroke_multiplier=entry.get("stroke", (1, 1)),
            apply_weighting=entry.get("weight", True),
            viewbox=entry.get("viewbox", DEFAULT_VIEWBOX),
        )

        # Sanity checking
        assert 0 not in radical.stroke_multiplier, "Multiplier of 0 probably unintended"

        if char is not None:
            radical_set.add(char)

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

    extractions = defaultdict(list)
    for entry in data["extraction"]:
        name = entry["name"]
        input = entry["input"]
        output = entry.get("output")
        element = entry["element"]

        if output is None:
            output = char_to_file(element)

        extractions[input].append(
            Extraction(
                name=name,
                input=input,
                output=output,
                element=element,
            )
        )

    radicals = list(map(make_radical, data["radical"]))
    characters = list(map(make_character, os.listdir(CHARACTER_DIRECTORY)))

    return KanjiData(
        radicals=radicals,
        radical_set=frozenset(radical_set),
        radical_names=radical_names,
        characters=characters,
        characters_exclude=frozenset(data["exclude"]),
        extractions=extractions,
    )
