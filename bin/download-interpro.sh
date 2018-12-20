#!/bin/bash

#SBATCH -J interpro
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -p normal
#SBATCH -t 24:00:00
#SBATCH -A iPlant-Collabs

set -u

METAGENOMES="metagenomes-4.1.csv"
INTERPRO_DIR="./interpro"
GO_DIR="./go"

[[ ! -d "$INTERPRO_DIR" ]] && mkdir -p "$INTERPRO_DIR"
[[ ! -d "$GO_DIR" ]]       && mkdir -p "$GO_DIR"

find "$INTERPRO_DIR" -type f -size 0 -delete
find "$GO_DIR" -type f -size 0 -delete

ACCS=$(mktemp)
awk -F',' 'NR>1 {print $1 "\t" $7}' "$METAGENOMES" | sed 's/"//g'  > "$ACCS"

JOBS='jobs'
cat /dev/null > "$JOBS"

i=0
while read -r ACC ERR; do
    i=$((i+1))
    #URL="https://www.ebi.ac.uk/metagenomics/api/v1/analyses/${ACC}/file/${ERR}_FASTA_InterPro.tsv.gz"
    #URL="https://www.ebi.ac.uk/metagenomics/api/v1/analyses/${ACC}/file/${ERR}_MERGED_FASTQ_GO.csv"

    URL="https://www.ebi.ac.uk/metagenomics/api/v1/analyses/${ACC}/file/${ERR}_MERGED_FASTQ_InterPro.tsv.gz"
    OUT_FILE="$OUT_DIR/$(basename "$URL")"

    #printf "%3d: %s\n" $i "$URL"

    echo "wget -nv -O $OUT_FILE --no-clobber $URL" >> "$JOBS"

    echo "curl -o $INTERPRO_DIR/ https://www.ebi.ac.uk/metagenomics/api/v1/analyses/${ACC}/interpro-identifiers
    if [[ $i -gt 5 ]]; then
        break
    fi
done < "$ACCS"

NJOBS=$(wc -l "$JOBS" | awk '{print $1}')
echo "NJOBS \"$NJOBS\""

parallel -j 10 < "$JOBS"

echo "Done."
