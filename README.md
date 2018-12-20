# Classification of Metagenomic Sample Biomes from Frequency of Interpro and GO Terms

# Author

Ken Youens-Clark <kyclark@email.arizona.edu>

# Samples

Samples were taken from EBI MGnify metagenome search for those
analyzed with pipeline 4.1 (data/metagenomes-4.1.csv). Use
"bin/ebi_download.py" to download the "interpro.tsv" files for each
sample which contain counts for both Interpro and GO accessions.

Get sample metadata with "bin/get-meta.py" and put into "data/meta".

Count GO/Interpro frequecies with count-accs.sh/parse_interpro.py.

Merge these into frequency matrices with "merge_counts.py".
