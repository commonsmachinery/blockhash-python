#! /usr/bin/env python
#
# Perceptual image hash calculation tool based on algorithm descibed in
# Block Mean Value Based Image Perceptual Hashing by Bian Yang, Fan Gu and Xiamu Niu
#
# Copyright 2014 Commons Machinery http://commonsmachinery.se/
# Distributed under an MIT license, please see LICENSE in the top dir.

import argparse
import PIL.Image as Image

def median1(data):
    data = sorted(data)
    length = len(data)
    if length % 2 == 0:
        return (data[length // 2] + data[length // 2 + 1]) / 2.0
    return data[length // 2]

def median2(data):
    data = sorted(data)
    length = len(data)
    return data[length // 2]

median = median2

def method1(data, size, bits):
    if size % (bits) != 0:
        raise RuntimeError('Unable to split image of size {}x{} into {}x{} identical non-overlapping blocks'.format(size, size, bits, bits))
    result = []
    blocksize = size // bits

    for y in range(bits):
        for x in range(bits):
            total = 0

            for iy in range(blocksize):
                for ix in range(blocksize):
                    r, g, b = data[x * blocksize + ix, y * blocksize + iy]
                    total += (r + g + b) / 3.0

            result.append(total)

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1
    return result

def method2(data, size, bits):
    if size % (bits + 1) != 0:
        raise RuntimeError('Unable to split image of size {}x{} into {}x{} identical overlapping blocks'.format(size, size, bits, bits))
    result = []
    overlap_size = size // (bits + 1)
    blocksize = overlap_size * 2

    for y in range(bits):
        for x in range(bits):
            total = 0

            for iy in range(blocksize):
                for ix in range(blocksize):
                    r, g, b = data[x * overlap_size + ix, y * overlap_size + iy]
                    total += (r + g + b) / 3.0

            result.append(total)

    m = median(result)
    for i in range(bits * bits):
        result[i] = 0 if result[i] < m else 1
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--method', type=int, default=1, choices=[1, 2],
        help='Use non-overlapping method (1) or overlapping (2). Default: 1')
    parser.add_argument('--interpolation', type=int, default=1, choices=[1, 2, 3, 4],
        help='Interpolation method: 1 - nearest neightbor, 2 - bilinear, 3 - bicubic, 4 - high-quality downsampling. Default: 1')
    parser.add_argument('--size', type=int, default=640, help='Resize the image to NxN pixels. Default: 640')
    parser.add_argument('--bits', type=int, default=16, help='Create hash of size NxN bits. Default: 16')
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
        im = im.resize((args.size, args.size), interpolation)

        # convert to RGB, making sure we ignore alpha channel
        # transparent pixels will become black
        im = im.convert('RGB')

        data = im.load()
        hash = method(data, args.size, args.bits)
        hash = ''.join([str(x) for x in hash])
        print('{} {}'.format(fn, hash))
