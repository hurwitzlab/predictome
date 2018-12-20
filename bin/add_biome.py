#!/usr/bin/env python3

import csv
import pandas as pd
import json
import os

def get(path, data):
    if not path or not data:
        return None

    while True:
        key = path.pop(0)
        if key in data:
            val = data[key]
            if path:  # still more to do
                data = val
            else:
                return val
        else:
            return None

def main():
    print('Reading metagenomes file')
    run_to_sample = {}
    with open('../data/metagenomes-4.1.csv', 'rt') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            run_to_sample[row['ENA run']] = row['Sample']

    meta_dir = '../data/meta'
    run_to_biome = {}
    biomes = {}
    for i, file in enumerate(os.scandir('../data/interpro-counts')):
        # ERR2245493_MERGED_FASTQ_InterPro.tsv => ERR2245493
        run_name, _ = os.path.splitext(file.name)
        run_name = run_name.split('_')[0]

        if not run_name in run_to_sample:
            print('Unknown run "{}"'.format(run_name))
            continue

        sample_name = run_to_sample[run_name]
        print('{:4}: {} => {}'.format(i + 1, run_name, sample_name))

        #
        # Find the sample JSON to get the biome name
        #
        sample_meta = os.path.join(meta_dir, sample_name + '.json')
        if not os.path.isfile(sample_meta):
            print('Cannot find sample meta "{}"'.format(sample_meta))
            continue

        meta = json.load(open(sample_meta))
        run_to_biome[run_name] = get(
            ['data', 'relationships', 'biome', 'data', 'id'], meta)

    biome_df = pd.DataFrame.from_dict(run_to_biome)
    print(biome_df)
    # df = pd.read_csv('../data/freqs/interpro.csv')

main()
