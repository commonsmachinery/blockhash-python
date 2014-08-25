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

def method_pixdiv(im, bits, overlap=True):
    data = im.getdata()
    width, height = im.size

    def onepass(block_width, block_height, x_offset, y_offset, maxblocks):
        blocks = [[0 for col in range(maxblocks)] for row in range(maxblocks)]

        for y in range(y_offset, height):
            y_frac, y_int = math.modf((y - y_offset + 1) % block_height)

            weight_top = (1 - y_frac)
            weight_bottom = (y_frac)

            # y_int will be 0 on bottom/right borders and on block boundaries
            if y_int > 0 or (y + 1) == height:
                block_top = block_bottom = int(math.floor(float(y - y_offset) / block_height))
            else:
                block_top = int(math.floor(float(y - y_offset) / block_height))
                block_bottom = int(math.ceil(float(y - y_offset) / block_height))

            # stop after reaching maxblocks, in case we're doing 4-pass analysis with overlapping blocks
            if block_bottom == maxblocks:
                break

            for x in range(x_offset, width):
                total = avg_value(im, data, x, y)
                x_frac, x_int = math.modf((x - x_offset + 1) % block_width)

                weight_left = (1 - x_frac)
                weight_right = (x_frac)

                # x_int will be 0 on bottom/right borders and on block boundaries
                if x_int > 0 or (x + 1) == width:
                    block_left = block_right = int(math.floor(float(x - x_offset) / block_width))
                else:
                    block_left = int(math.floor(float(x - x_offset) / block_width))
                    block_right = int(math.ceil(float(x - x_offset) / block_width))

                # stop after reaching maxblocks, in case we're doing 4-pass analysis with overlapping blocks
                if block_right == maxblocks:
                    break

                # add weighted pixel value to relevant blocks
                blocks[block_top][block_left] += total * weight_top * weight_left
                blocks[block_top][block_right] += total * weight_top * weight_right
                blocks[block_bottom][block_left] += total * weight_bottom * weight_left
                blocks[block_bottom][block_right] += total * weight_bottom * weight_right

        return blocks

    if overlap:
        overlap_width = float(width) / (bits + 1)
        overlap_height = float(height) / (bits + 1)
        block_width = overlap_width * 2
        block_height = overlap_height * 2

        blocks1 = onepass(block_width, block_height, 0, 0, bits // 2)
        blocks2 = onepass(block_width, block_height, int(overlap_width), 0, bits // 2)
        blocks3 = onepass(block_width, block_height, 0, int(overlap_height), bits // 2)
        blocks4 = onepass(block_width, block_height, int(overlap_width), int(overlap_height), bits // 2)

        result = []
        for row in range(0, bits // 2):
            for col in range(bits // 2):
                result.append(blocks1[row][col])
                result.append(blocks2[row][col])
            for col in range(bits // 2):
                result.append(blocks3[row][col])
                result.append(blocks4[row][col])
    else:
        block_width = float(width) / bits
        block_height = float(height) / bits

        blocks = onepass(block_width, block_height, 0, 0, bits)
        result = [blocks[row][col] for row in range(bits) for col in range(bits)]

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1
    return result

def method3(im, bits):
    return method_pixdiv(im, bits, overlap=False)

def method4(im, bits):
    return method_pixdiv(im, bits, overlap=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--method', type=int, default=1, choices=[1, 2, 3, 4],
        help='Use non-overlapping method (1), overlapping (2), pixdiv (3), overlapping pixdiv (4). Default: 1')
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
        method = method3
    elif args.method == 4:
        method = method4

    for fn in args.filenames:
        im = Image.open(fn)

        # convert indexed/grayscale images to RGB
        if im.mode == '1' or im.mode == 'L' or im.mode == 'P':
            im = im.convert('RGB')
        elif im.mode == 'LA':
            im = im.convert('RGBA')

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