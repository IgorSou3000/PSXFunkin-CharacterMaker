import json
import os
import subprocess
import glob

from spritesheetprocessor import SpritesheetProcessor
from characterjson import CharacterJSON
from spritepacker import SpritePacker
from util import *

"""
Parses the Psych engine character json

TODO: Add the FNF 0.4 json support
"""
class PsychJSON():
    def __init__(self, data):
        self.data = data

        self.image_name = os.path.basename(self.data["image"])
        self.scale = self.data["scale"]

# Main entry point.
if __name__ == "__main__":
    for chr_path in glob.glob("**/*.chr.json", recursive=True):
        directory_name = os.path.dirname(chr_path) + "/"

        # Open the character chr.json
        with open(chr_path) as file:
            character_json = CharacterJSON(json.load(file))

        # Open the fnf character .json
        with open(directory_name + character_json.fnf_json) as file:
            json_file = PsychJSON(json.load(file))

        EXPORT_PATH = character_json.output_path + "/"
        SPRITESHEET_PATH = directory_name + json_file.image_name
        IMAGE_TEST = EXPORT_PATH + json_file.image_name + ".test" + ".png"

        if not file_need_update(chr_path, EXPORT_PATH + os.path.basename(chr_path) + ".h"):
            continue

        print("")
        print(f"Character .chr.json path: {chr_path}")
        print(f"Character .json path: {directory_name}{character_json.fnf_json}")
        print(f"Character bpp: {character_json.bpp}")
        print(f"Character scale: {character_json.image_scale}\n")

        SpritePacker.create_output_directory(EXPORT_PATH)
        character = SpritesheetProcessor(SPRITESHEET_PATH, character_json.flip_x, character_json.image_scale, character_json.xml_scale)

        character.resize_spritesheet(json_file.scale * PSXFUNKIN_SCALE)
        character.quantize_spritesheet(IMAGE_TEST, character_json.bpp ** 2)
        character.load_animation_data(character_json.fnf_animations, json_file.data["animations"])
        character.load_xml_data(
            character_json.psxfunkin_animations, 
            character_json.indices,
            json_file.scale
        )

        SpritePacker.create_images(character.sprites, character.spritesheet_image, EXPORT_PATH, character_json.bpp)
        SpritePacker.create_images_text(character.sprites, character.spritesheet_image, EXPORT_PATH, character_json.dict["vram_position"], character_json.dict["bpp"])
        SpritePacker.create_header_file(EXPORT_PATH + os.path.basename(chr_path), character.sprites, character_json.name)