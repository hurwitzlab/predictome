#!/usr/bin/env python3
"""
Author : kyclark
Date   : 2018-10-29
Purpose: Merge GO/Interpro counts for each sample into a frequency matrix
"""

import argparse
import csv
import json
import numpy as np
import os
import pandas as pd
import re
import sys
from collections import defaultdict


# --------------------------------------------------
def get_args():
    """get args"""
    parser = argparse.ArgumentParser(
        description='Merge GO terms into a frequence matrix',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        'indir',
        help='Directory of Interpro/GO counts',
        metavar='DIR',
        type=str)

    parser.add_argument(
        '-m',
        '--metagenomes',
        help='Location of metagenomes-4.1.csv',
        metavar='FILE',
        type=str,
        default='../data/metagenomes-4.1.csv')

    parser.add_argument(
        '-d',
        '--meta_dir',
        help='Dir with sample metadata JSON',
        metavar='DIR',
        type=str,
        default='../data/meta')

    parser.add_argument(
        '-n',
        '--normalize',
        help='Normalize count: log, tf, nlog_tf, aug_freq',
        metavar='str',
        type=str,
        default=None)

    parser.add_argument(
        '-o',
        '--outfile',
        help='Output matrix file',
        metavar='FILE',
        type=str,
        default=None)

    parser.add_argument('--no_overwrite', action='store_true')

    return parser.parse_args()


# --------------------------------------------------
def warn(msg):
    """Print a message to STDERR"""
    print(msg, file=sys.stderr)


# --------------------------------------------------
def die(msg='Something bad happened'):
    """warn() and exit with error"""
    warn(msg)
    sys.exit(1)


# --------------------------------------------------
def find_dirs(in_dir):
    if not os.path.isdir(in_dir):
        die('"{}" is not a directory'.format(in_dir))

    dirs = []
    for path in os.scandir(in_dir):
        if path.is_dir():
            dirs.append(path.path)

    if not dirs:
        die('Found no subdirectories in "{}"'.format(in_dir))

    return dirs


# --------------------------------------------------
def get(path, data):
    if not path or not data:
        return 'NA'

    while True:
        key = path.pop(0)
        if key in data:
            val = data[key]
            if path:  # still more to do
                data = val
            else:
                return val
        else:
            return 'NA'


# --------------------------------------------------
def main():
    """main"""
    args = get_args()
    in_dir = args.indir
    out_file = args.outfile
    meta_dir = args.meta_dir
    metagenomes = args.metagenomes
    normalize = args.normalize

    if not in_dir:
        die('Missing --indir argument')

    if not meta_dir:
        die('Missing --meta_dir argument')

    if os.path.isfile(out_file) and args.no_overwrite:
        msg = '--outfile "{}" exists and --no_overwrite true so exiting'
        die(msg.format(out_file))

    if not os.path.isdir(meta_dir):
        die('--meta_dir {} is not a directory'.format(meta_dir))

    out_dir = os.path.dirname(os.path.abspath(out_file))
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    # Interpro/GO are for runs, we need to get the sample names
    # for the meta JSON in order to know the biome name
    print('Reading metagenomes file')
    run_to_sample = {}
    with open(metagenomes, 'rt') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            run_to_sample[row['ENA run']] = row['Sample']

    samples = []
    all_accs = set()
    run_to_biome = []
    counts = []

    print('Looking for files in "{}"'.format(in_dir))
    for i, file in enumerate(os.scandir(in_dir)):
        run_name, _ = os.path.splitext(file.name)

        # ERR2245493_MERGED_FASTQ_InterPro.tsv => ERR2245493
        run_name = run_name.split('_')[0]

        if not run_name in run_to_sample:
            warn('Unknown run "{}"'.format(run_name))
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
        run_to_biome.append(
            (run_name,
             get(['data', 'relationships', 'biome', 'data', 'id'], meta)))

        #
        # Read the acc,counts from file
        # Rename the "counts" column to the run name for later merging
        #
        df = pd.read_csv(file.path)
        df.columns = ['acc', run_name]
        counts.append(df)

        #
        # Note all the unique accessions
        #
        for acc in df['acc']:
            all_accs.add(acc)

        # if i == 2:
        #     break

    # print(samples)

    #
    # Create a new DataFrame with the unique, sorted accessions
    #
    accessions = sorted(all_accs)
    matrix = pd.DataFrame({'acc': accessions})

    #
    # Merge all the count DFs on the accessions
    #
    print('Merging data frames (this will probably take a while...)')
    num_dfs = len(counts)
    for i, count_df in enumerate(counts):
        print('{:<70}'.format('{}/{}'.format(i + 1, num_dfs)), end='\r')
        matrix = pd.merge(matrix, count_df, on='acc', how='outer').fillna(0)

    print()

    #
    # Transpose the matrix so that the accessions (Interpro/GO) which were
    # the rows become the columns (features), create a new "biome" column
    #
    print('Transposing matrix')
    #matrix = matrix.T.drop('acc')
    #matrix.columns = ['sample'] + accessions
    #matrix['biome'] = 'NA'

    #matrix = matrix.set_index('acc').T.reset_index()
    #matrix.columns = ['sample'] + (matrix.columns.tolist())[1:]

    matrix = matrix.set_index('acc').T.reset_index()
    #matrix = matrix.T.drop('acc').reset_index()
    matrix.columns = ['sample'] + accessions

    #
    # Set the biome values
    #
    print('Setting the biome names')

    biomes = pd.DataFrame({
        'sample': list(map(lambda t: t[0], run_to_biome)),
        'biome': list(map(lambda t: t[1], run_to_biome))
    })

    matrix = pd.merge(matrix, biomes, on='sample', how='inner').fillna('NA')

    #
    # Save to a new file
    #
    n_rows, n_cols = matrix.shape
    print('Writing {} rows, {} cols to file {}'.format(n_rows, n_cols,
                                                       out_file))
    matrix.to_csv(out_file, sep=',', index=False, header=True, encoding='utf-8')
    print('Done.')


# --------------------------------------------------
if __name__ == '__main__':
    main()
