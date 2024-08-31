import os
from dataclasses import dataclass
from PIL import Image

MAX_WIDTH_PER_IMAGE = 256
MAX_HEIGHT_IMAGE = 256

""" Class that creates the files that the PSXFunkin needs such .png .png.txt and .h """
class SpritePacker():
    @staticmethod
    def create_output_directory(output_directory_path):
        if not os.path.exists(output_directory_path):
                os.makedirs(output_directory_path)

    @staticmethod
    def create_images(sprites_list, spritesheet_image, output_directory_path, bpp):
        current_x = 0
        current_y = 0
        max_y = 0
        current_image = Image.new("RGBA", (MAX_WIDTH_PER_IMAGE, MAX_HEIGHT_IMAGE))
        current_number = 0
        previous_name = sprites_list[0].name

        for sprite in sprites_list:
            sprite_image = spritesheet_image.crop((sprite.x, sprite.y, sprite.x + sprite.w, sprite.y + sprite.h))

            if sprite.rotated:
                sprite_image = sprite_image.transpose(Image.ROTATE_90)
                sprite.w, sprite.h = sprite.h, sprite_w

            if sprite.h > max_y:
                max_y = sprite.h
                
            if current_x + sprite.w >= MAX_WIDTH_PER_IMAGE:
                current_x = 0
                current_y += max_y + 1
                max_y = sprite.h

            if previous_name != sprite.name:
                current_image = SpritePacker._change_image_size(current_image, bpp)
                current_image.save(os.path.join(output_directory_path, f"{previous_name.lower()}{str(current_number)}.png"))
                current_image = Image.new("RGBA", (MAX_WIDTH_PER_IMAGE, MAX_HEIGHT_IMAGE))
                current_x = 0
                current_y = max_y = 0
                max_y = sprite.h
                current_number = 0
                previous_name = sprite.name

            elif current_y + max_y >= MAX_WIDTH_PER_IMAGE:
                current_image = SpritePacker._change_image_size(current_image, bpp)
                current_image.save(os.path.join(output_directory_path, f"{sprite.name.lower()}{str(current_number)}.png"))

                current_image = Image.new("RGBA", (MAX_WIDTH_PER_IMAGE, MAX_HEIGHT_IMAGE))
                current_x = 0
                current_y = max_y = 0
                current_number += 1

            if sprite == sprites_list[-1]:
                current_image.paste(sprite_image, (current_x, current_y))

                current_image = SpritePacker._change_image_size(current_image, bpp)
                current_image.save(os.path.join(output_directory_path, f"{sprite.name.lower()}{str(current_number)}.png"))
                current_image = Image.new("RGBA", (MAX_WIDTH_PER_IMAGE, MAX_HEIGHT_IMAGE))

            sprite.name = sprite.name + str(current_number)
            sprite.x = current_x
            sprite.y = current_y

            current_image.paste(sprite_image, (current_x, current_y))

            current_x += sprite.w

    @staticmethod
    def create_images_text(sprites_list, spritesheet_image, output_directory_path, vram_position, bpp):
        previous_name = ""
        for sprite in sprites_list:
            if sprite.name == previous_name:
                continue

            previous_name = sprite.name

            with open(output_directory_path + sprite.name.lower() + ".png" ".txt", "w") as txt_file:
                for position in vram_position:
                    txt_file.write(str(position) + " ")

                txt_file.write(str(bpp))


    @staticmethod
    def create_header_file(path, sprites_list, character_name):
        with open(path + ".h", "w") as header_file:
            previous_name = ""

            header_file.write("enum\n{\n")

            for sprite in sprites_list:
                if sprite.name == previous_name:
                    continue

                name = character_name + "_ArcMain_" + sprite.name
                header_file.write(f"\t{name},\n")

                previous_name = sprite.name

            header_file.write("\n\t" + character_name + "_Arc_Max,\n")
            header_file.write("};\n\n")

            header_file.write(f"//{character_name} definitions\n")
            header_file.write(f"static const CharFrame char_{character_name.lower()}_frame[] = {{\n")
            for sprite in sprites_list:
                name = character_name + "_ArcMain_" + sprite.name
                header_file.write(f"\t{{{name}, {{{sprite.x:3d}, {sprite.y:3d}, {sprite.w:3d}, {sprite.h:3d}}},{{{sprite.pos_x:3d},{sprite.pos_y:3d}}}}},\n")

            header_file.write("};\n\n");

            header_file.write("\tconst char **pathp = (const char *[]){\n")

            for sprite in sprites_list:
                if sprite.name == previous_name:
                    continue

                name = '"' + sprite.name.lower() + ".tim" + '"'
                header_file.write("\t\t" + name + ",\n")

                previous_name = sprite.name

            header_file.write("\t\tNULL,\n")
            header_file.write("\t};")

            header_file.write("\n\n");
            header_file.write(f"iso/characters/{character_name.lower()}/main.arc: ");

            for sprite in sprites_list:
                if sprite.name == previous_name:
                    continue

                name = f"iso/characters/{character_name.lower()}/{sprite.name.lower()}.tim"
                header_file.write(f"{name} ")

                previous_name = sprite.name


    @staticmethod
    def _change_image_size(image, bpp):
        width_multiple = 4 if bpp == 4 else 2

        x, y, width, height = image.getbbox()

        width -= x
        height -= y
        
        width += 1
        height += 1

        width_remainder = width % width_multiple

        if width_remainder != 0:
            width = width + (width_multiple - width_remainder)

        return image.crop((x, y, x + width, y + height))
