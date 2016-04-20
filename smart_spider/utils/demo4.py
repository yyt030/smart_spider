#!/usr/bin/env python
# coding: utf8
__author__ = 'yueyt'

import pytesseract
from PIL import Image, ImageFilter


def prepare_image(img):
    """Transform image to greyscale and blur it"""
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    if 'L' != img.mode:
        img = img.convert('L')
    return img


def remove_noise(img, pass_factor):
    for column in range(img.size[0]):
        for line in range(img.size[1]):
            value = remove_noise_by_pixel(img, column, line, pass_factor)
            img.putpixel((column, line), value)
    return img


def remove_noise_by_pixel(img, column, line, pass_factor):
    if img.getpixel((column, line)) < pass_factor:
        return (0)
    return (255)


if __name__ == "__main__":
    for i in xrange(10):
        input_image = 'source_pic/%d.png' % i

        img = Image.open(input_image)
        img = prepare_image(img)
        img = remove_noise(img, 185)
        print input_image, '-' * 10, pytesseract.image_to_string(img)
        # img.show()
