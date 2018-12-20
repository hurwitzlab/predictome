#!/usr/bin/env python3
"""
Author : kyclark
Date   : 2018-12-13
Purpose: Rock the Casbah
"""

import argparse
import csv
import json
import os
import re
import requests
import sys
import subprocess


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    #parser.add_argument(
    #    'file', metavar='FILE', help='A positional argument')

    # parser.add_argument(
    #     '-a',
    #     '--arg',
    #     help='A named string argument',
    #     metavar='str',
    #     type=str,
    #     default='')

    # parser.add_argument(
    #     '-i',
    #     '--int',
    #     help='A named integer argument',
    #     metavar='int',
    #     type=int,
    #     default=0)

    # parser.add_argument(
    #     '-f', '--flag', help='A boolean flag', action='store_true')

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
def main():
    """Make a jazz noise here"""
    args = get_args()
    file = '../data/metagenomes-4.1.csv'
    njobs = 10
    #interpro_dir = os.path.join(os.getcwd(), 'interpro')
    interpro_dir = '../data/interpro'

    if not os.path.isdir(interpro_dir):
        os.makedirs(interpro_dir)

    tmpl = 'https://www.ebi.ac.uk/metagenomics/api/v1/analyses/{}/downloads'
    interpro_re = re.compile('interpro\.tsv', re.IGNORECASE)

    jobs_file = os.path.join(os.getcwd(), 'jobs.txt')
    jobs_fh = open(jobs_file, 'wt')

    with open(file) as fh:
        reader = csv.DictReader(fh)
        for i, row in enumerate(reader):
            analysis = row['Analysis']
            print('{:3}: {}'.format(i+1, analysis))
            url = tmpl.format(analysis)
            r = requests.get(url)
            dat = json.loads(r.text)
            files = dat['data']
            if not files:
                continue

            for file in files:
                match = interpro_re.search(file['id'])
                if match:
                    file_url = file['links']['self']
                    basename = os.path.basename(file_url)
                    fpath = os.path.join(interpro_dir, basename)
                    jobs_fh.write('wget -nv -O {} --no-clobber {}\n'.format(
                        fpath, file_url))

    jobs_fh.close()

    cmd = 'parallel -j {} < {}'.format(njobs, jobs_file)
    subprocess.run(cmd, shell=True)
    print('Done')


# --------------------------------------------------
if __name__ == '__main__':
    main()
