#!/bin/bash

#SBATCH -J count
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p normal
#SBATCH -t 24:00:00
#SBATCH -A iPlant-Collabs

set -u

IN_DIR="../data/interpro"
INTERPRO_DIR="../data/interpro-counts"
GO_DIR="../data/go-counts"
JOBS_RUN=50

FILES=$(mktemp)
find "$IN_DIR" -type f > "$FILES"

JOBS=$(mktemp)
cat /dev/null > "$JOBS"

while read -r FILE; do
    echo "time ./parse_interpro.py -i $INTERPRO_DIR -g $GO_DIR $FILE" >> "$JOBS"
done < "$FILES"

NJOBS=$(wc -l "$JOBS" | awk '{print $1}')

if [[ $NJOBS -gt 0 ]]; then
    echo "Running NJOBS \"$NJOBS\""
    parallel -j $JOBS_RUN < "$JOBS"
fi

echo "Done."
