#!/usr/bin/env python3

import csv
import os
import requests


def main():
    url = 'https://www.ebi.ac.uk/metagenomics/api/v1/samples/{}'
    out_dir = '../data/meta'

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    with open('../data/metagenomes-4.1.csv', 'rt') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            sample = row['Sample']
            print('{:3}: {}'.format(i+1, sample))

            out_file = os.path.join(out_dir, sample + '.json')
            if not os.path.isfile(out_file):
                r = requests.get(url.format(sample))
                with open(out_file, 'wt') as out_fh:
                    out_fh.write(r.text)

    print('Done')

main()
