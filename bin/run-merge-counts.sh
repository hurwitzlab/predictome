#!/bin/bash

#SBATCH -J interpro
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p normal
#SBATCH -t 24:00:00
#SBATCH -A iPlant-Collabs

./merge_counts.py -o ../data/freqs/interpro.csv -m ../data/metagenomes-4.1.csv -d ../data/meta ../data/interpro-counts

./merge_counts.py -o ../data/freqs/go.csv -m ../data/metagenomes-4.1.csv -d ../data/meta ../data/go-counts
