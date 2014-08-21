#! /usr/bin/env python
#
# Perceptual image hash calculation tool based on algorithm descibed in
# Block Mean Value Based Image Perceptual Hashing by Bian Yang, Fan Gu and Xiamu Niu
#
# Copyright 2014 Commons Machinery http://commonsmachinery.se/
# Distributed under an MIT license, please see LICENSE in the top dir.

import math
import argparse
import PIL.Image as Image

def median(data):
    data = sorted(data)
    length = len(data)
    if length % 2 == 0:
        return (data[length // 2] + data[length // 2 + 1]) / 2.0
    return data[length // 2]

def avg_value(im, data, x, y):
    width, height = im.size

    pix = data[y * width + x]
    result = None

    if im.mode == 'RGBA':
        r, g, b, a = pix
        result = (r + g + b + a) / 4.0
    elif im.mode == 'RGB':
        r, g, b = pix
        a = 255
        result = (r + g + b + a) / 4.0
    else:
        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

    return result

def method1(im, bits):
    data = im.getdata()
    width, height = im.size
    blocksize_x = width // bits
    blocksize_y = height // bits

    result = []

    for y in range(bits):
        for x in range(bits):
            total = 0

            for iy in range(blocksize_y):
                for ix in range(blocksize_x):
                    cx = x * blocksize_x + ix
                    cy = y * blocksize_y + iy
                    total += avg_value(im, data, cx, cy)

            result.append(total)

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1

    return result

def method2(im, bits):
    data = im.getdata()
    width, height = im.size
    overlap_x = width // (bits + 1)
    overlap_y = height // (bits + 1)
    blocksize_x = overlap_x * 2
    blocksize_y = overlap_y * 2

    result = []

    for y in range(bits):
        for x in range(bits):
            total = 0

            for iy in range(blocksize_y):
                for ix in range(blocksize_x):
                    cx = x * overlap_x + ix
                    cy = y * overlap_y + iy
                    total += avg_value(im, data, cx, cy)

            result.append(total)

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1
    return result

def method1_pixdiv(im, bits):
    data = im.getdata()
    width, height = im.size
    block_width = float(width) / bits
    block_height = float(height) / bits

    blocks = [[0 for col in range(bits)] for row in range(bits)]

    for y in range(height):
        y_frac, y_int = math.modf((y + 1) % block_height)

        weight_top = (1 - y_frac)
        weight_bottom = (y_frac)

        # y_int will be 0 on bottom/right borders and on block boundaries
        if y_int > 0 or (y + 1) == height:
            block_top = block_bottom = int(math.floor(float(y) / block_height))
        else:
            block_top = int(math.floor(float(y) / block_height))
            block_bottom = int(math.ceil(float(y) / block_height))

        for x in range(width):
            total = avg_value(im, data, x, y)
            x_frac, x_int = math.modf((x + 1) % block_width)

            weight_left = (1 - x_frac)
            weight_right = (x_frac)

            # x_int will be 0 on bottom/right borders and on block boundaries
            if x_int > 0 or (x + 1) == width:
                block_left = block_right = int(math.floor(float(x) / block_width))
            else:
                block_left = int(math.floor(float(x) / block_width))
                block_right = int(math.ceil(float(x) / block_width))

            # add weighted pixel value to relevant blocks
            blocks[block_top][block_left] += total * weight_top * weight_left
            blocks[block_top][block_right] += total * weight_top * weight_right
            blocks[block_bottom][block_left] += total * weight_bottom * weight_left
            blocks[block_bottom][block_right] += total * weight_bottom * weight_right

    result = [blocks[row][col] for row in range(bits) for col in range(bits)]

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--method', type=int, default=1, choices=[1, 2, 3],
        help='Use non-overlapping method (1), overlapping (2), pixdiv (3). Default: 1')
    parser.add_argument('--bits', type=int, default=16,
        help='Create hash of size N^2 bits. Default: 16')
    parser.add_argument('--size',
        help='Resize image to specified size before hashing, e.g. 256x256')
    parser.add_argument('--interpolation', type=int, default=1, choices=[1, 2, 3, 4],
        help='Interpolation method: 1 - nearest neightbor, 2 - bilinear, 3 - bicubic, 4 - antialias. Default: 1')
    parser.add_argument('--debug', action='store_true',
        help='Print hashes as 2D maps (for debugging)')
    parser.add_argument('filenames', nargs='+')

    args = parser.parse_args()

    if args.interpolation == 1:
        interpolation = Image.NEAREST
    elif args.interpolation == 2:
        interpolation = Image.BILINEAR
    elif args.interpolation == 3:
        interpolation = Image.BICUBIC
    elif args.interpolation == 4:
        interpolation = Image.ANTIALIAS

    if args.method == 1:
        method = method1
    elif args.method == 2:
        method = method2
    elif args.method == 3:
        method = method1_pixdiv

    for fn in args.filenames:
        im = Image.open(fn)

        # convert indexed/grayscale images to RGB
        if im.mode == 'L' or im.mode == 'P':
            im = im.convert('RGB')

        if args.size:
            size = args.size.split('x')
            size = (int(size[0]), int(size[1]))
            im = im.resize(size, interpolation)

        hash = method(im, args.bits)
        hash = ''.join([str(x) for x in hash])

        print('{} {}'.format(fn, hash))

        if args.debug:
            map = [hash[i:i+args.bits] for i in range(0, len(hash), args.bits)]
            print("")
            print("\n".join(map))
            print("")