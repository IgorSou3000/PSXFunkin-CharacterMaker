import json
import os
import subprocess
import glob
import math
import re
import xml.etree.ElementTree as ET
from PIL import Image
from util import *

# Since it only FNF spritesheet, i will disable the max pixels to avoid any errors of massive spritesheets
Image.MAX_IMAGE_PIXELS = None

class SpritesheetProcessor:
    """Class that contains and process the character's spritesheet data."""
    def __init__(self, path: str, flip_x: bool, image_scale: float, xml_scale: float) -> None:
        # Load the character's spritesheet image and XML data
        self.spritesheet_image = Image.open(path + ".png")
        self.original_spritesheet_image = Image.open(path + ".png")  # Copy for me able to use the original dimensions
        self.spritesheet_xml = ET.parse(path + ".xml").getroot()

        # Scale options
        self.image_scale = image_scale
        self.xml_scale = xml_scale

        # Extra options
        self.flip_x = flip_x

        # Animation data
        self.animation_names = []
        self.animation_offsets = []
        
        self.sprites = []

        # Flip the image horizontally if required
        if self.flip_x:
            self.spritesheet_image = self.spritesheet_image.transpose(Image.FLIP_LEFT_RIGHT)

    def resize_spritesheet(self, scale: float) -> None:
        """Resize the spritesheet and set the scale if needed."""
        if self.image_scale == -1:
            self.image_scale = scale

        if self.xml_scale == -1:
            self.xml_scale = scale

        width = round(self.spritesheet_image.size[0] * self.image_scale)
        height = round(self.spritesheet_image.size[1] * self.image_scale)

        self.spritesheet_image = self.spritesheet_image.resize((width, height))

    def quantize_spritesheet(self, temp_path: str, colors: int) -> None:
        """Quantize the spritesheet and remove any semi-transparent pixels."""
        alpha = self.spritesheet_image.getchannel("A").point(lambda p: 255 if p >= 128 else 0)
        self.spritesheet_image.putalpha(alpha)

        self.spritesheet_image.save(temp_path)

        subprocess.run([
            "src/pngquant.exe",
            "--force",
            "--nofs",
            "--posterize", "3"
            "--verbose", str(colors),
            "--ext", ".png", f"{temp_path}"
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        self.spritesheet_image = Image.open(temp_path)

    def load_animation_data(self, requested_animations, available_animations) -> None:
        """Get the requested animation names and offsets."""
        available_anim_names = [anim["anim"] for anim in available_animations]

        for anim_name in requested_animations:
            if anim_name not in available_anim_names:
                raise RuntimeError(f"Failed to find animation {anim_name}")

            for anim in available_animations:
                if anim_name == anim["anim"]:
                    self.animation_names.append(anim["name"])
                    self.animation_offsets.append(anim["offsets"])

    def load_xml_data(self, animation_list, indices_list, json_scale: int) -> None:
        """Get the requested XML sprite coordinates."""
        frame_x_min = min([int(sub_texture.get("frameX", 0)) for sub_texture in self.spritesheet_xml.findall("SubTexture")])
        frame_y_min = min([int(sub_texture.get("frameY", 0)) for sub_texture in self.spritesheet_xml.findall("SubTexture")])

        offset_x_min = min([i[0] for i in self.animation_offsets])
        offset_y_min = min([i[1] for i in self.animation_offsets])

        for anim_name, anim_offsets, anim_list, indices in zip(self.animation_names, self.animation_offsets, animation_list, indices_list):
            index = 0
            temp_sprite_list = []
            anim_name_without_numbers = re.sub(r"\d+$", "", anim_name)

            for sub_texture in self.spritesheet_xml.findall("SubTexture"):
                sub_texture_name_without_numbers = re.sub(r"\d+$", "", sub_texture.get("name"))

                # Skip if the animation names are different
                if re.match(anim_name_without_numbers, sub_texture_name_without_numbers) is None:
                    continue

                x = float(sub_texture.get("x"))
                y = float(sub_texture.get("y"))
                width = float(sub_texture.get("width"))
                height = float(sub_texture.get("height"))

                frame_x = float(sub_texture.get("frameX", 0))
                frame_y = float(sub_texture.get("frameY", 0))

                # Adjust x coordinate for flipped sprites
                if self.flip_x:
                    x = self.original_spritesheet_image.size[0] - x - width

                sprite = Sprite(
                    anim_list,
                    round(x * self.xml_scale),
                    round(y * self.xml_scale),
                    int(width * self.xml_scale),
                    int(height * self.xml_scale),
                    round((frame_x - frame_x_min + ((anim_offsets[0] - offset_x_min) / json_scale)) * self.xml_scale),
                    round((frame_y - frame_y_min + ((anim_offsets[1] - offset_y_min) / json_scale)) * self.xml_scale),
                    bool(sub_texture.get("rotated", False))
                )

                # Skip if the sprite already exists in the list
                if sprite in temp_sprite_list:
                    continue

                temp_sprite_list.append(sprite)
                index += 1

            for idx in indices:
                try:
                    self.sprites.append(temp_sprite_list[idx])
                except IndexError:
                    raise IndexError(f"\n\nThe {anim_list} index '{idx}' doesn't exist in {anim_name}") from None

            # Add all sprites if no specific indices are provided
            if not indices:
                self.sprites.extend(temp_sprite_list)

        self._remove_empty_space_from_sprites()

    def _remove_empty_space_from_sprites(self) -> None:
        """Remove any empty space that a sprite has."""
        for sprite in self.sprites:
            image = self.spritesheet_image.crop((sprite.x, sprite.y, sprite.x + sprite.w, sprite.y + sprite.h))
            x, y, width, height = image.getbbox()

        for sprite in self.sprites:
            image = self.spritesheet_image.crop((sprite.x, sprite.y, sprite.x + sprite.w, sprite.y + sprite.h))
            x, y, width, height = image.getbbox()

            width -= x
            height -= y

            sprite.x += x
            sprite.y += y
            sprite.w = width
            sprite.h = height

            sprite.pos_x += int(self.sprites[0].w / 2) - x
            sprite.pos_y += self.sprites[0].h - y