Hail-Annotate
=======

**Hail-Annotate** is a Python library that annotates variant call format (VCF) files with GnomAD allele frequency information.
This repo assumes the user is familiar with the variant call format (link) and the GnomAD Project (link).

Paths for GnomAD v2.1.1 data hosted on GCP:
- Project Bucket: gs://gcp-public-data--gnomad/release/
- Genomes: gs://gcp-public-data--gnomad/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht
- Exomes: gs://gcp-public-data--gnomad/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht/

Config should have the following keys:
- Exomes path (path)
    Ideally this is Google Cloud path to your GnomAD Exomes Data
- Genomes path (path)
    Ideally this is Google Cloud path to your GnomAD Genomes Data
- tmp cache_dir (path)
    This directory will contain temporary output files for your data.
- test_mode boolean
    If True, will subset your data to only values on chr22 to run a smaller test set.

The Final Pipeline
	1. Set up a Google cloud bucket to hold your data, mine is `gs://hail-annotation-scripts/Hail-Annotate/`
    2. If you haven't, configure a Google dataproc service account and allow is to access this bucket.
	2. Configure the input params for the Google cloud bucket at modules/wrapper.py.
	3. Clone this repo to the Google Cloud Bucket.
	4. Initiate a dataproc instance with `hailctl dataproc start brad-test --region us-west1`
	5. Submit my job to the dataproc cluster using `hailctl dataproc submit brad-test /Users/bbowles/Documents/Code/Hail-Annotate/modules/wrapper.py --region us-west1 --max-idle=10m`
		a. This will copy the repo from Google cloud to the local dataproc instance
		b. The dataproc will then execute Hail annotation scripts
		c. The dataproc will save an output file to HDFS and then copy it to Google Cloud
	6. Stop the dataproc instance: `hailctl dataproc stop brad-test --region us-west1`
	7. Check for lingering instances:
		a. `gcloud dataproc clusters list --region=us-west1`  
		b. `gcloud compute instances list`


