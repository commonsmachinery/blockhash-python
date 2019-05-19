#! /usr/bin/env python
#
# Perceptual image hash calculation tool based on algorithm descibed in
# Block Mean Value Based Image Perceptual Hashing by Bian Yang, Fan Gu and Xiamu Niu
#
# Copyright 2014 Commons Machinery http://commonsmachinery.se/
# Distributed under an MIT license, please see LICENSE in the top dir.

import argparse
import PIL.Image as Image

from blockhash import blockhash


def main():
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

        print('{hash}  {fn}'.format(fn=fn, hash=hash))

        if args.debug:
            bin_hash = '{:0{width}b}'.format(int(hash, 16), width=args.bits ** 2)
            map = [bin_hash[i:i+args.bits] for i in range(0, len(bin_hash), args.bits)]
            print("")
            print("\n".join(map))
            print("")


if __name__ == '__main__':
    main()
