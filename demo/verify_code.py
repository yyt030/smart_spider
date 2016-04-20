#!/usr/bin/env python
# coding: utf8
__author__ = 'yueyt'

import pytesseract
import re
from PIL import Image, ImageEnhance


def cut(img, start_heigth, end_heigth):
    (width, heigth) = img.size
    pixels = img.load()

    for w in xrange(width):
        for h in xrange(heigth):
            if start_heigth <= h <= end_heigth:
                pass
            else:
                pixels[w, h] = 255
    return img


def binaryzation(img):
    pixdata = img.load()
    (width, height) = img.size
    threshold = 230

    for w in xrange(width):
        for h in xrange(height):
            if pixdata[w, h] > threshold:
                # 大于阈值的置为背景色，否则置为前景色（文字的颜色）
                pixdata[w, h] = 255
            else:
                pixdata[w, h] = 0
    return img


def verify(img):
    image = Image.open(img)

    image = image.convert('L')
    image = cut(image, 18, 45)
    brightness = ImageEnhance.Brightness(image)
    image = brightness.enhance(1.3)  # 亮度增强
    image = binaryzation(image)  # 二值化

    reg = re.compile("[‘'\-< _;%?!(:,@~]+")
    return reg.sub('', pytesseract.image_to_string(image, lang='eng'))
