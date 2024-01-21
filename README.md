# Hail-Annotate
Use cloud infrastructure to annotate input VCF files with GnomAD allele frequency information.

Paths for GnomAD v2.1.1 data hosted on AWS:
- Project Bucket: s3://gnomad-public-us-east-1/release/
- Genomes: s3://gnomad-public-us-east-1/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht
- Exomes: s3://gnomad-public-us-east-1/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht/

Paths for GnomAD v2.1.1 data hosted on GCP:
- Project Bucket: gs://gcp-public-data--gnomad/release/
- Genomes: gs://gcp-public-data--gnomad/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht
- Exomes: gs://gcp-public-data--gnomad/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht/

Config should have the following keys:
- Exomes path
- Genomes path
- tmp cache_dir
- test_mode boolean (subsets to chr22 if needed)

