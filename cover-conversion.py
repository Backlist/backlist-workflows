#!/usr/bin/env python3

import sys

from PIL import Image

COVER_HEIGHT = 480


def gather_covers(input_files):
    result = []

    for input_file in input_files:
        img = Image.open(input_file)

        orig_width, orig_height = img.size
        new_height = COVER_HEIGHT
        new_width = COVER_HEIGHT * (orig_width / orig_height)

        img = img.resize((int(new_width), int(new_height)), Image.BICUBIC)
        if img.mode == 'P':
            img = img.convert(mode='RGBA', dither=None)

        result.append(img)

    return result


if __name__ == '__main__':
    covers = gather_covers(sys.argv[1:])

    for idx, cover in enumerate(covers):
        cover.save("output/cover-{}.jpg".format(idx), 'JPEG', quality=70)
