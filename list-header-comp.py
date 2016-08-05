#!/usr/bin/env python3

import random
import sys

from PIL import Image

COVER_HEIGHT = 480
BACKGROUND_COLOR = (39, 46, 111, 255)


def build_header_strip(covers):
    composite_width = get_composite_width(covers)
    header_strip = Image.new(
        mode='RGBA',
        size=(composite_width, COVER_HEIGHT),
        color=(0, 0, 0, 0))

    x_offset = 0
    for idx, cover in enumerate(covers):
        paste_frame = set_up_cover_paste(cover, x_offset)
        header_strip.paste(cover, paste_frame)

        x_offset += cover.size[0]

    return header_strip


def gather_covers(input_files):
    result = []

    for input_file in input_files:
        img = Image.open(input_file)

        orig_width, orig_height = img.size
        new_height = COVER_HEIGHT
        new_width = COVER_HEIGHT * (orig_width / orig_height)

        img = img.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
        if img.mode == 'P':
            img = img.convert(mode='RGBA', dither=None)

        result.append(img)

    return result


def get_composite_width(covers):
    width = 0
    for cover in covers:
        width += cover.size[0]

    return width


def set_up_cover_paste(cover, x_offset):
    return (x_offset, 0, x_offset + cover.size[0], cover.size[1])


if __name__ == '__main__':
    # Get cover images
    covers = gather_covers(sys.argv[1:])

    header = build_header_strip(covers)

    header.save('output/list-header.jpg', 'JPEG', quality=50)
