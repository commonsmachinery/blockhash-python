#! /usr/bin/env python
#
# Perceptual image hash calculation tool based on algorithm descibed in
# Block Mean Value Based Image Perceptual Hashing by Bian Yang, Fan Gu and Xiamu Niu
#
# Copyright 2014 Commons Machinery http://commonsmachinery.se/
# Distributed under an MIT license, please see LICENSE in the top dir.

import argparse
import PIL.Image as Image

def median(data):
    data = sorted(data)
    length = len(data)
    if length % 2 == 0:
        return (data[length // 2] + data[length // 2 + 1]) / 2.0
    return data[length // 2]

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
                    pix = data[cy * width + cx]

                    if im.mode == 'L':
                        total += pix
                    elif im.mode == 'RGBA':
                        r, g, b, a = pix
                        total += (r + g + b + a) / 4.0
                    elif im.mode == 'RGB':
                        r, g, b = pix
                        a = 255
                        total += (r + g + b + a) / 4.0
                    else:
                        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

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
                    pix = data[cy * width + cx]

                    if im.mode == 'L':
                        total += pix
                    elif im.mode == 'RGBA':
                        r, g, b, a = pix
                        total += (r + g + b + a) / 4.0
                    elif im.mode == 'RGB':
                        r, g, b = pix
                        a = 255
                        total += (r + g + b + a) / 4.0
                    else:
                        raise RuntimeError('Unsupported image mode: {}'.format(im.mode))

            result.append(total)

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--method', type=int, default=1, choices=[1, 2],
        help='Use non-overlapping method (1) or overlapping (2). Default: 1')
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

    for fn in args.filenames:
        im = Image.open(fn)
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