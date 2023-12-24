#!/usr/bin/env python

"""
Converts between characters and their hex representation, and vice eversa.
"""

import sys


def hex_to_char(s):
    return chr(int(s, 16))


def char_to_hex(c):
    return f"{ord(c):05x}"


def char_to_file(c):
    return f"{char_to_hex(c)}.svg"


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if len(arg) == 1:
            print(char_to_hex(arg))
        else:
            print(hex_to_char(arg))
