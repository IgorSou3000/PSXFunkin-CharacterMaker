import sys
from util import *

DEFAULT_PLAYER_VRAM = [448, 0, 0, 480]
DEFAULT_OPPONENT_VRAM = [448, 256, 0, 481]
DEFAULT_GF_VRAM = [512, 0, 16, 480]

""" The .chr.json class"""
class CharacterJSON():
    def __init__(self, data):
        self.data = data

        self.dict = {
        "animations" : json_get_key(data, "animations", True),
        "json_path" : json_get_key(data, "json_path", True),
        "output_path" : json_get_key(data, "output_path", True),
        "image_scale" : json_get_key(data, "image_scale", False),
        "xml_scale" : json_get_key(data, "xml_scale", False),
        "flip_x" : json_get_key(data, "flip_x", False, False),
        "bpp" : json_get_key(data, "bpp", True),
        "vram_position" : json_get_key(data, "vram_position", True),
        "name" : json_get_key(data, "name", True),
        }

        # Animations section
        self.fnf_animations = [item["fnf_name"] for item in self.dict["animations"]]
        self.psxfunkin_animations = [item["psxfunkin_name"] for item in self.dict["animations"]]
        self.indices = [item.get("indices", []) for item in self.dict["animations"]]

        self.fnf_json = data["json_path"]
        self.output_path = data["output_path"]
        self.image_scale = data.get("image_scale", -1)
        self.xml_scale = data.get("xml_scale", -1)
        self.flip_x = data.get("flip_x", False)
        self.bpp = data["bpp"]
        self.vram_position = data.get("vram_position", "opponent")
        self.name = data["name"]

        self._check_errors()

    def _check_errors(self):
        if self.dict["bpp"] not in (4, 8):
            sys.exit("The BPP needs to be 4 (16 colors) or 8 (256 colors)")

        if self.dict["vram_position"] == "player":
            self.dict["vram_position"] = DEFAULT_PLAYER_VRAM

        elif self.dict["vram_position"] == "opponent":
            self.dict["vram_position"] = DEFAULT_OPPONENT_VRAM

        elif self.dict["vram_position"] == "gf":
            self.dict["vram_position"] = DEFAULT_GF_VRAM

        elif not isinstance(self.dict["vram_position"], list) or len(self.dict["vram_position"]) != 4:
            sys.exit(
            """
            The vram position needs to have 4 values:

            'vram_position' : {texture_x texture_y palette_x palette_y}

            or use some of these strings

            'vram_position' : 'player'
            'vram_position' : 'opponent'
            'vram_position' : 'gf'
            """
        )