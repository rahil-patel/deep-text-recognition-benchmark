#!/usr/bin/env python
"""Script to generate input for lmdb creatrion from annotation data

Usage:
    prepare_dataset.py FOLDER_PATH

Arguments:
    FOLDER_PATH                  Path to folder

"""

import glob
import shutil
from os.path import exists, basename, splitext, join
import os
from collections import defaultdict
import random
from subprocess import Popen

from PIL import Image


def main():
    dataset_folder = join(DATA, 'price_dataset')

    if exists(dataset_folder):
        shutil.rmtree(dataset_folder)

    os.makedirs(join(dataset_folder, 'train'))
    os.makedirs(join(dataset_folder, 'val'))
    os.makedirs(join(dataset_folder, 'query'))

    dataset = {}
    char_counts = defaultdict(int)
    for gt_path in glob.glob(join(DATA, '*_gt.txt')):
        img_path = gt_path.replace('_gt.txt', '.jpg')
        name = splitext(basename(img_path))[0]
        img = Image.open(img_path)

        for line in open(gt_path):
            try:
                x, y, w, h, text = line.strip().split()
                text = text.lower()
            except:
                print(line)
                continue

            if text != '0' * 12 and not (text.startswith('$') or (text[:-1].isdigit() and text.endswith('c'))):
                continue

            if int(w) <=1 or int(h) <= 1:
                continue

            if 'f' in text:
                from IPython.core.debugger import Tracer; Tracer()()

            if text == '0' * 12:
                split = 'query'
            else:
                split = 'train' if random.random() < 0.8 else 'val'

            x, y, w, h = int(x), int(y), int(w), int(h)
            crop = img.crop((x, y, x + w, y + h))

            crop_path = join(split, f'{name}--{x}-{y}-{w}-{h}.jpg')
            crop.save(join(dataset_folder, crop_path))
            dataset.setdefault(split, []).append((crop_path, text))

            if split == 'train':
                for ch in text:
                    char_counts[ch] += 1

    for split, data in dataset.items():
        gt_path = join(dataset_folder, f'{split}.txt')
        with open(gt_path, 'w') as f:
            for path, text in data:
                f.write(f'{path}\t{text}\n')

        ps = Popen(f'python create_lmdb_dataset.py --inputPath {dataset_folder} --gtFile {gt_path} --outputPath {dataset_folder}/{split}_lmdb', shell=True)
        ps.communicate()

    with open(join(dataset_folder, 'chars.txt'), 'w') as f:
        f.write('{}'.format(''.join(sorted([ch for ch, count in char_counts.items() if count > 10]))))

    ignore_lbls = [ch for ch, count in char_counts.items() if count <= 10]
    if ignore_lbls:
        print(''.join(sorted(ignore_lbls)), ' have insufficient samples')


if __name__ == '__main__':
    from docopt import docopt
    arguments = docopt(__doc__)

    DATA = arguments['FOLDER_PATH']
    main()
