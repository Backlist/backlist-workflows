#!/usr/bin/env python3

import sys

from PIL import Image

COVER_HEIGHT = 480
BORDER_WIDTH = 10
BACKGROUND_COLOR = (39, 46, 111, 0)


def gather_covers(input_files):
    '''Given a list of files, return a list of resized RGB images'''
    result = []

    for input_file in sys.argv[1:]:
        img = Image.open(input_file)

        orig_width, orig_height = img.size
        new_height = COVER_HEIGHT
        new_width = COVER_HEIGHT * (orig_width / orig_height)

        img = img.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
        if img.mode == 'P':
            img = img.convert(mode='RGB', dither=None)

        result.append(img)

    return result


def get_composite_width(covers):
    '''Given a list of images, return composite width including borders'''
    width = BORDER_WIDTH
    for cover in covers:
        width += cover.size[0] + BORDER_WIDTH

    return width


def set_up_cover_paste(cover, x_offset):
    '''Given cover image and offset, define inputs for next cover placement'''
    crop_frame = (0, 0, cover.size[0], cover.size[1])
    cover_region = cover.crop(crop_frame)

    paste_frame = \
        (x_offset, BORDER_WIDTH,
            x_offset + cover.size[0], COVER_HEIGHT + BORDER_WIDTH)

    return (cover_region, paste_frame)


if __name__ == '__main__':
    covers = gather_covers(sys.argv[1:])

    composite_width = get_composite_width(covers)

    composite = Image.new(
        mode='RGB',
        size=(composite_width, COVER_HEIGHT + (2 * BORDER_WIDTH)),
        color=BACKGROUND_COLOR)

    x_offset = BORDER_WIDTH
    for idx, cover in enumerate(covers):
        cover_region, paste_frame = set_up_cover_paste(cover, x_offset)
        composite.paste(cover_region, paste_frame)

        # Move next x draw position over one cover and one border
        x_offset += cover.size[0] + BORDER_WIDTH

    composite.save('twitter-cover-image.jpg', 'JPEG', quality=70)
