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

def total_value_rgba(im, data, x, y):
    r, g, b, a = data[y * im.size[0] + x]
    if a == 0:
        return 765
    else:
        return r + g + b

def total_value_rgb(im, data, x, y):
    r, g, b = data[y * im.size[0] + x]
    return r + g + b

def bits_to_hexhash(bits):
    return '{0:0={width}x}'.format(int(''.join([str(x) for x in bits]), 2), width = len(bits) // 4)


def blockhash_even(im, bits):
    if im.mode == 'RGBA':
        total_value = total_value_rgba
    elif im.mode == 'RGB':
        total_value = total_value_rgb
    else:
        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

    data = im.getdata()
    width, height = im.size
    blocksize_x = width // bits
    blocksize_y = height // bits

    result = []

    for y in range(bits):
        for x in range(bits):
            value = 0

            for iy in range(blocksize_y):
                for ix in range(blocksize_x):
                    cx = x * blocksize_x + ix
                    cy = y * blocksize_y + iy
                    value += total_value(im, data, cx, cy)

            result.append(value)

    m = []
    for i in range(4):
        m.append(median(result[i*bits*bits//4:i*bits*bits//4+bits*bits//4]))

    for i in range(bits * bits):
        if (((result[i] < m[0]) and (i < bits*bits/4)) or
            ((result[i] < m[1]) and (i >= bits*bits/4) and (i < bits*bits/2)) or
            ((result[i] < m[2]) and (i >= bits*bits/2) and (i < bits*bits/4+bits*bits/2)) or
            ((result[i] < m[3]) and (i >= bits*bits/2+bits*bits/4))):
            result[i] = 0
        else:
            result[i] = 1

    return bits_to_hexhash(result)

def blockhash(im, bits):
    if im.mode == 'RGBA':
        total_value = total_value_rgba
    elif im.mode == 'RGB':
        total_value = total_value_rgb
    else:
        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

    data = im.getdata()
    width, height = im.size

    even_x = width % bits == 0
    even_y = height % bits == 0

    if even_x and even_y:
        return blockhash_even(im, bits)

    blocks = [[0 for col in range(bits)] for row in range(bits)]

    block_width = float(width) / bits
    block_height = float(height) / bits

    for y in range(height):
        if even_y:
            # don't bother dividing y, if the size evenly divides by bits
            block_top = block_bottom = int(y // block_height)
            weight_top, weight_bottom = 1, 0
        else:
            y_frac, y_int = math.modf((y + 1) % block_height)

            weight_top = (1 - y_frac)
            weight_bottom = (y_frac)

            # y_int will be 0 on bottom/right borders and on block boundaries
            if y_int > 0 or (y + 1) == height:
                block_top = block_bottom = int(y // block_height)
            else:
                block_top = int(y // block_height)
                block_bottom = int(-(-y // block_height)) # int(math.ceil(float(y) / block_height))

        for x in range(width):
            value = total_value(im, data, x, y)

            if even_x:
                # don't bother dividing x, if the size evenly divides by bits
                block_left = block_right = int(x // block_width)
                weight_left, weight_right = 1, 0
            else:
                x_frac, x_int = math.modf((x + 1) % block_width)

                weight_left = (1 - x_frac)
                weight_right = (x_frac)

                # x_int will be 0 on bottom/right borders and on block boundaries
                if x_int > 0 or (x + 1) == width:
                    block_left = block_right = int(x // block_width)
                else:
                    block_left = int(x // block_width)
                    block_right = int(-(-x // block_width)) # int(math.ceil(float(x) / block_width))

            # add weighted pixel value to relevant blocks
            blocks[block_top][block_left] += value * weight_top * weight_left
            blocks[block_top][block_right] += value * weight_top * weight_right
            blocks[block_bottom][block_left] += value * weight_bottom * weight_left
            blocks[block_bottom][block_right] += value * weight_bottom * weight_right

    result = [blocks[row][col] for row in range(bits) for col in range(bits)]

    m = []
    for i in range(4):
        m.append(median(result[i*bits*bits//4:i*bits*bits//4+bits*bits//4]))

    for i in range(bits * bits):
        if (((result[i] < m[0]) and (i < bits*bits/4)) or
            ((result[i] < m[1]) and (i >= bits*bits/4) and (i < bits*bits/2)) or
            ((result[i] < m[2]) and (i >= bits*bits/2) and (i < bits*bits/4+bits*bits/2)) or
            ((result[i] < m[3]) and (i >= bits*bits/2+bits*bits/4))):
            result[i] = 0
        else:
            result[i] = 1

    return bits_to_hexhash(result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--quick', type=bool, default=False,
        help='Use quick hashing method. Default: False')
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

    if args.quick:
        method = blockhash_even
    else:
        method = blockhash

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

        print('{} {}'.format(fn, hash))

        if args.debug:
            bin_hash = bin(int(hash, 16))[2:]
            map = [bin_hash[i:i+args.bits] for i in range(0, len(bin_hash), args.bits)]
            print("")
            print("\n".join(map))
            print("")
