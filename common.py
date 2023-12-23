import tomllib
from collections import namedtuple
from xml.etree import ElementTree

"""
Common functions and concepts used by multiple scripts
"""

DEFAULT_WIDTH = 109
DEFAULT_HEIGHT = 109
DEFAULT_VIEWBOX = f"0 0 {DEFAULT_WIDTH} {DEFAULT_HEIGHT}"

KanjiData = namedtuple("KanjiData", ("radicals",))
Radical = namedtuple(
    "Radical", ("char", "file", "x", "y", "width", "height", "viewbox"),
)


def read_data(path="data.toml"):
    with open(path, "rb") as file:
        data = tomllib.load(file)

    def make(entry):
        char = entry["char"]
        return Radical(
            char=char,
            file=entry.get("file", f"{ord(char):05x}.svg"),
            x=entry["x"],
            y=entry["y"],
            width=entry.get("width", DEFAULT_WIDTH),
            height=entry.get("height", DEFAULT_HEIGHT),
            viewbox=entry.get("viewbox", DEFAULT_VIEWBOX),
        )

    radicals = list(map(make, data["radicals"]))
    return KanjiData(radicals=radicals)


def parse_xml(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    return tree, root
