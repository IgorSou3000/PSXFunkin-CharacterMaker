import os
import sys
from dataclasses import dataclass

# Sprites on PSXFunkin are scaled by 0.25 when comparing with the FNF sprites.
PSXFUNKIN_SCALE = 0.25

""" Class for each sprite of the character """
@dataclass
class Sprite():
    name : str

    x : int
    y : int
    w : int
    h : int

    pos_x : int
    pos_y : int

    rotated : bool = False

    def __eq__(self, other):
        return (
            self.x == other.x and self.y == other.y and
            self.w == other.w and self.h == other.h
        )

def file_need_update(source, dest):
    source_time = os.path.getmtime(source)
    dest_time = os.path.getmtime(dest) if os.path.isfile(dest) else 0

    return source_time > dest_time

def json_get_key(json_data, key : str, is_required : bool, default_value = None):
    if is_required:
        try:
            return json_data[key]
        except KeyError:
            sys.exit(f"The key '{key}' is required")

    return json_data.get(key, default_value)

