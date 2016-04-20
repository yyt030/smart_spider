#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A simple captcha recognition demo by python-tesseract"""

import urllib2

import pytesseract
import re
from PIL import ImageDraw, Image, ImageEnhance

headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
           'Referer': ""}


def get_batch_pic(url, dir):
    for i in range(10):
        print "download", i
        filename = "%d.jpg" % (i)
        picfile = os.path.join(dir, filename)

        req = urllib2.Request(url, headers=headers)
        file(picfile, "wb").write(urllib2.urlopen(req).read())


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


def binaryzation_test(img):
    pixdata = img.load()
    (width, height) = img.size
    threshold = 230
    BACKCOLOR = (255, 255, 255)  # 白
    TEXTCOLOR = (0, 0, 0)  # 黑
    for i in xrange(width):
        for j in xrange(height):
            if j == 5 and i == 50:
                pixdata[i, j] = TEXTCOLOR
            else:
                pixdata[i, j] = BACKCOLOR

    return img


def Enhance(image):
    '''分离有效信息和干扰信息'''
    pixels = image.load()
    new_image = image.copy()
    new_pixels = new_image.load()
    (width, height) = image.size

    xx = [1, 0, -1, 0, 1, -1, 1, -1]
    yy = [0, 1, 0, -1, -1, 1, 1, -1]

    Threshold = 50

    Window = []
    for i in xrange(width):
        for j in xrange(height):
            Window = [i, j]
            for k in xrange(8):  # 取3*3窗口中像素值存在Window中
                if 0 <= i + xx[k] < width and 0 <= j + yy[k] < height:
                    Window.append((i + xx[k], j + yy[k]))
            Window.sort()
            (x, y) = Window[len(Window) / 2]
            if (pixels[x, y] - pixels[i, j] < Threshold):  # 若差值小于阈值则进行“强化”
                if pixels[i, j] < 255 - pixels[i, j]:  # 若该点接近黑色则将其置为黑色（0），否则置为白色（255）
                    new_pixels[i, j] = 0
                else:
                    new_pixels[i, j] = 255
            else:
                new_pixels[i, j] = pixels[i, j]
    return new_image


def enhance_test(image):
    """ 去除干扰点 """
    pixels = image.load()
    new_image = image.copy()
    new_pixels = new_image.load()
    (width, height) = image.size

    xx = [1, 0, -1, 0, 1, -1, 1, -1]
    yy = [0, 1, 0, -1, -1, 1, 1, -1]

    threshold = 40

    for w in xrange(width):
        for h in xrange(height):
            window = []  # 3*3 窗口中的像素值存入window
            over_threshold_num = 0
            for k in xrange(8):  # 3*3
                if 0 <= w + xx[k] < width and 0 <= h + yy[k] < height:
                    window.append(pixels[w + xx[k], h + yy[k]])
                    if abs(pixels[w + xx[k], h + yy[k]] - pixels[w, h]) > threshold:
                        over_threshold_num += 1
                        # print window
                if over_threshold_num >= 4:
                    new_pixels[w, h] = 255

    return new_image


def Smooth(Picture):
    '''平滑降噪'''
    Pixels = Picture.load()
    (Width, Height) = Picture.size

    xx = [1, 0, -1, 0]
    yy = [0, 1, 0, -1]
    BACKCOLOR = (255, 255, 255)

    for i in xrange(Width):
        for j in xrange(Height):
            if Pixels[i, j] != BACKCOLOR:
                Count = 0
                for k in xrange(4):
                    try:
                        if Pixels[i + xx[k], j + yy[k]] == BACKCOLOR:
                            Count += 1
                    except IndexError:  # 忽略访问越界的情况
                        pass
                if Count > 3:
                    Pixels[i, j] = BACKCOLOR
    return Picture


def Zhifang(im):
    width, height = im.size
    pix = im.load()
    a = [0] * 256
    for w in xrange(width):
        for h in xrange(height):
            p = pix[w, h]
            a[p] = a[p] + 1

    s = max(a)
    print a, len(a), s  # 长度256,a保存的分别是颜色范围0-255出现的次数
    image = Image.new('RGB', (256, 256), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    for k in range(256):
        # print k,a[k],a[k]*200/s
        a[k] = a[k] * 200 / s  # 映射范围0-200
        source = (k, 255)  # 起点坐标y=255, x=[0,1,2....]
        target = (k, 255 - a[k])  # 终点坐标y=255-a[x],a[x]的最大数值是200,x=[0,1,2....]
        draw.line([source, target], (100, 100, 100))
    return im


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


def threshold(filename, limit=100):
    """Make text more clear by thresholding all pixels above / below this limit to white / black
    """
    # read in colour channels
    img = Image.open(filename)
    # resize to make more clearer
    m = 1.5
    img = img.resize((int(img.size[0] * m), int(img.size[1] * m))).convert('RGBA')
    pixdata = img.load()

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y][0] < limit:
                # make dark color black
                pixdata[x, y] = (0, 0, 0, 255)
            else:
                # make light color white
                pixdata[x, y] = (255, 255, 255, 255)
    # img.save('tmp/threshold_' + filename)
    return img.convert('L')  # convert image to single channel greyscale


if __name__ == '__main__':
    reg = re.compile("[‘'\- _;%?!(:,@~]+")
    n = 0
    all_num = 502
    import os

    for i in xrange(all_num, all_num + 1):
        image_file = 'source_pic/%d.png' % i
        if not os.path.isfile(image_file):
            continue
        image = Image.open(image_file)

        image = image.convert('L')
        image = cut(image, 18, 45)

        brightness = ImageEnhance.Brightness(image)
        image = brightness.enhance(1.3)  # 亮度增强
        image = binaryzation(image)  # 二值化

        result = pytesseract.image_to_string(image, lang='eng')
        result = reg.sub('', result)
        print image_file, '-' * 10, result
        if len(result) == 6:
            n += 1
    print '=' * 10, n, all_num
