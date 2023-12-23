import tomllib
from dataclasses import dataclass
from typing import Optional
from xml.etree.ElementTree import Element

"""
Code to read the data file for kanji processing.
"""

KanjiData = namedtuple("KanjiData", ("radicals",))
Radical = namedtuple("Radical", ("char", "file", "image"))


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


def read_data(path="data.toml"):
    with open(path, "rb") as file:
        data = tomllib.load(file)

    def make(entry):
        char = entry["char"]  # XXX opt
        image = SubImage(
            x=entry["x"],
            y=entry["y"],
            width=entry.get("width", DEFAULT_WIDTH),
            height=entry.get("height", DEFAULT_HEIGHT),
            viewbox=entry.get("viewbox", DEFAULT_VIEWBOX),
        )
        return Radical(
            char=char,
            file=entry.get("file", f"{ord(char):05x}.svg"),
            image=image,
        )

    radicals = list(map(make, data["radicals"]))
    return KanjiData(radicals=radicals)
