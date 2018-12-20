#!/usr/bin/env python3
"""
Author : kyclark
Date   : 2018-12-13
Purpose: Parse Interpro file for counts of Interpro and GO accessions
"""

import argparse
import csv
import gzip
import os
import sys
from collections import Counter


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Count of Interpro and GO accessions',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('file', metavar='FILE', help='Interpro report')

    parser.add_argument(
        '-i',
        '--interpro_dir',
        help='Directory to write Interpro counts',
        metavar='DIR',
        type=str,
        default=None)

    parser.add_argument(
        '-g',
        '--go_dir',
        help='Directory to write GO counts',
        metavar='DIR',
        type=str,
        default=None)

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
def write_counts(counts, out_path):
    if counts:
        out_fh = open(out_path, 'wt')
        out_fh.write(','.join(['acc', 'count']) + '\n')

        for acc, count in counts.items():
            out_fh.write(','.join([acc, str(count)]) + '\n')

        out_fh.close()

    return 1


# --------------------------------------------------
def main():
    """Make a jazz noise here"""
    args = get_args()
    in_file = args.file
    interpro_out_dir = args.interpro_dir
    go_out_dir = args.go_dir

    #interpro_in_dir = os.path.join(os.getcwd(), '../data/interpro')
    #interpro_out_dir = os.path.join(os.getcwd(), '../data/interpro-counts')
    #go_out_dir = os.path.join(os.getcwd(), '../data/go-counts')

    if not os.path.isfile(in_file):
        die('"{}" is not a file'.format(in_file))

    if not os.path.isdir(interpro_out_dir):
        os.makedirs(interpro_out_dir)

    if not os.path.isdir(go_out_dir):
        os.makedirs(go_out_dir)

    flds = [
        'prot_acc', 'seq_md5', 'seq_len', 'analysis', 'sig_acc', 'sig_desc',
        'start', 'stop', 'score', 'status', 'date_run', 'ip_acc', 'ip_annot',
        'go_annot', 'pathway_annot'
    ]

    # ERR2245493_MERGED_FASTQ_InterPro.tsv.gz => ERR2245493
    basename = os.path.basename(in_file)
    print('Processing {}'.format(basename))
    sample = basename.split('_')[0]
    _, ext = os.path.splitext(basename)

    fh = gzip.open(in_file, 'rt') if ext == '.gz' else open(in_file, 'rt')

    interpro = Counter()
    go = Counter()

    hdr = fh.readline()
    for line in fh:
        row = line.rstrip('\n').split('\t')
        nflds = len(row)
        
        if nflds > 11:
            ip_acc = row[11]
            if ip_acc:
                interpro.update([ip_acc])

        if nflds > 13:
            go_annot = row[13]
            if go_annot:
                go.update(go_annot.split('|'))

    # reader = csv.DictReader(fh, delimiter='\t', fieldnames=flds)
    # for row in reader:
    #     if 'ip_acc' in row:
    #         ip_acc = row['ip_acc']
    #         if ip_acc:
    #             interpro.update([ip_acc])

    #     if 'go_annot' in row:
    #         go_annot = row['go_annot']
    #         if go_annot:
    #             go.update(go_annot.split('|'))

    write_counts(
        counts=interpro,
        out_path=os.path.join(interpro_out_dir, sample + '.csv'))

    write_counts(counts=go, out_path=os.path.join(go_out_dir, sample + '.csv'))

    print('Done')


# --------------------------------------------------
if __name__ == '__main__':
    main()
