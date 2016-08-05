#!/usr/bin/env python3

import random
import sys

from PIL import Image, ImageDraw

IMG_WIDTH = 1200
IMG_HEIGHT = 630
COVER_WIDTH = int(IMG_WIDTH / 4)
BACKGROUND_COLOR = (39, 46, 111, 255)
OVERLAY_COLOR = (39, 46, 111, 220)


def build_canvas(cover_strip):
    '''Size and create an offscreen canvas based on cover strip size.'''
    return Image.new(
        mode='RGBA',
        size=(IMG_WIDTH + (2 * COVER_WIDTH), cover_strip.size[1] * 2),
        color=(0, 0, 0, 0))


def build_cover_strip(covers):
    '''Assemble covers in a vertical strip to be repeated.'''
    composite_height = get_composite_height(covers)
    cover_strip = Image.new(
        mode='RGBA',
        size=(COVER_WIDTH, composite_height),
        color=BACKGROUND_COLOR)

    y_offset = 0
    for idx, cover in enumerate(covers):
        paste_frame = set_up_cover_paste(cover, y_offset)
        cover_strip.paste(cover, paste_frame)

        y_offset += cover.size[1]

    return cover_strip


def build_logo():
    '''Open Backlist logo to insert.'''
    return Image.open('avatar-300.png')


def calculate_offsets(canvas, cover_strip):
    '''
    Calculate the offsets based on size of offscreen canvas
    and cover strip.
    '''
    centered_offset = int((canvas.size[1] - cover_strip.size[1]) / 2)

    y_offsets = []
    multipliers = [0, 0.5, 1, 1.5]
    random.shuffle(multipliers)

    for i in range(6):
        y_offsets.append(int(centered_offset * multipliers[i % 4]))

    return (centered_offset, y_offsets)


def composite_image(canvas, cover_strip):
    '''
    Primary drawing logic aligns cover strips with Backlist logo in
    preparation for cropping.
    '''
    # Set up frames for compositing
    centered_offset, y_offsets = calculate_offsets(canvas, cover_strip)

    for idx, y_offset in enumerate(y_offsets):
        paste_region = set_up_strip_paste(
            cover_strip, idx * COVER_WIDTH, y_offset)
        canvas.paste(cover_strip, paste_region)
        if y_offset == 0:
            logo = build_logo()
            overlay = build_canvas(cover_strip)
            context = ImageDraw.Draw(overlay, mode='RGBA')
            context.rectangle(paste_region, OVERLAY_COLOR)
            canvas = Image.alpha_composite(canvas, overlay)
            canvas.paste(logo,
                         (idx * COVER_WIDTH,
                          cover_strip.size[1],
                          idx * COVER_WIDTH + logo.size[0],
                          cover_strip.size[1] + logo.size[1]))

    canvas = canvas.rotate(random.randrange(-20, 20, 5),
                           resample=Image.BICUBIC,
                           expand=True)

    return canvas


def finish_image(canvas, idx):
    '''Perform the final crop on the canvas and save a JPEG'''
    left = int((canvas.size[0] - IMG_WIDTH) / 2)
    top = int((canvas.size[1] - IMG_HEIGHT) / 2)
    right = left + IMG_WIDTH
    bottom = top + IMG_HEIGHT
    canvas = canvas.crop((left, top, right, bottom))
    canvas.save("output/social-card-{}.jpg".format(idx), 'JPEG', quality=90)


def gather_covers(input_files):
    '''Given a list of files, return a list of resized RGB images'''
    result = []

    for input_file in input_files:
        img = Image.open(input_file)

        orig_width, orig_height = img.size
        new_width = COVER_WIDTH
        new_height = COVER_WIDTH * (orig_height / orig_width)

        img = img.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
        if img.mode == 'P':
            img = img.convert(mode='RGBA', dither=None)

        result.append(img)

    return result


def get_composite_height(covers):
    '''Given a list of images, return composite height'''
    height = 0
    for cover in covers:
        height += cover.size[1]

    return height


def set_up_cover_paste(cover, y_offset):
    '''Given cover image and offset, define inputs for next cover placement'''
    paste_frame = \
        (0, y_offset,
            0 + cover.size[0], y_offset + cover.size[1])

    return paste_frame


def set_up_strip_paste(cover_strip, x_offset, y_offset):
    '''Calculate the paste region'''
    left = x_offset
    right = x_offset + COVER_WIDTH
    top = y_offset
    bottom = y_offset + cover_strip.size[1]

    return (left, top, right, bottom)


if __name__ == '__main__':
    # Number of images to output
    count = int(sys.argv[1])

    # Get cover images
    covers = gather_covers(sys.argv[2:])

    # Loop number of times specified in command line arguments
    for i in range(count):
        random.shuffle(covers)

        # Create an image of the covers in a vertical strip
        # to repeat in composite
        cover_strip = build_cover_strip(covers)

        # Create the primary offscreen drawing canvas and fill with background
        canvas = build_canvas(cover_strip)
        context = ImageDraw.Draw(canvas)
        context.rectangle(
            (0, 0, canvas.size[0], canvas.size[1]), BACKGROUND_COLOR)

        canvas = composite_image(canvas, cover_strip)

        finish_image(canvas, i)
