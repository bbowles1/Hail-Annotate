Launching Computing Tasks
==========================

Installing Hail
---------------

Hail provides a wrapper for Google Dataproc, `hailctl` which provisions Dataproc clusters which already contain Hail installations. This saves us the trouble of setting up Hail on our own Dataproc clusters, although we will still need Hail on our local computer to initiate such instances. Users can install Hail using their favorite package manager (I have used both pip and conda). More detailed instructions on downloading Hail can be found `here <https://hail.is/#install>`_.


Hail Annotation Scripts
------------------------
This guide makes use of several annotation scripts which are designed to take input VCF information and annotate them with GnomAD information. I am specificially interested in annotating input VCF files with information on exome and genome frequency in Hail v2.1.1, although this code is readily adaptable to other Hail releases.

This repository has several files used to execute this pipeline:
1. app.py
2. config.json
3. modules/wrapper.py --> series of scripts used to download input data to the dataproc cluster and upload output data.
4. hail_annotation.py

These files will take an input VCF file stored in your Google Cloud bucket and annotate it with variant allele frequency information from the GnomAD exome and genome datasets specified by the `config.json`. The resulting output file will then be uploaded back to your Google Cloud Bucket.


Editing Input Parameters
-------------------------
Users will need to edit this repository's `config.json` file to specify which versions of Hail exome/genome data they wish to use for annotation. The json has the following structure:

.. code-block:: python

    {"exomes": {
        "path" : "gs://gcp-public-data--gnomad/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht/"
    },
    "genomes": {
        "path" : "gs://gcp-public-data--gnomad/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht"
    },
    "cache": {
        "path" : "/tmp/"
    },
    "testing" : false
    }

In this json, we are providing the google cloud paths to GnomAD exome and genome data. Additionally, the `cache` key is the directory to which our dataproc instance will write intermediate data (I recommend leaving it as "/tmp/"). Lastly, if the `testing` key is set to `true`, our script will subset input VCF data to chromosome 22 variants. This provides a more lightweight execution of our annotation pipeline that is useful for debugging while minimizing computing/storage costs.


Uploading Scripts to Google Cloud
---------------------------------
Once you configure your `config.json`, you will need to upload the following miminal set of files to the Google Cloud bucket that we created for this project:
- your input VCF
- app.py
- config.json
- the full /modules/ directory

Users can also copy the full repo to your cloud storage bucket using `gsutil cp -r ./Hail-Annotate gs://your-bucket-name/Hail-Annotate/`.


Creating DataProc Instances
---------------------------
Now that we've set up our Cloud project, bucket, and service account, and uploaded the required scripts and input files, we can now start initiating DataProc computing tasks.

1. Create a Dataproc instance.

.. code-block::bash

    hailctl dataproc start gnomad-test \
        --region us-west1 \
        --service-account=test-service-account@your-project.iam.gserviceaccount.com

2. Submit your Job to the Cluster.

.. code-block:: bash

    hailctl dataproc submit gnomad-test \
        /local/path/to/Hail-Annotate/modules/wrapper.py \
        --region us-west1 --max-idle=10m

This will copy the repo from Google cloud to the local dataproc instance.
The dataproc will then execute Hail annotation scripts.
The dataproc will save an output file to HDFS and then copy it to Google Cloud.

3. Wait for annotation to complete. An output file ??? will be uploaded to your Google Cloud bucket.

4. The Dataproc instance should stop automatically. Confirm that your instance is no longer running using the below commands:

.. code-block:: bash

    gcloud dataproc clusters list --region=us-west1
    
    gcloud compute instances list --region=us-west1

If your instance has not stopped running, you can manually shut it down using:

.. code-block:: bash

    hailctl dataproc stop gnomad-test --region us-west1

5. *Optional:* Clean up Google Cloud Bucket.
Your Google Cloud bucket will accumulate storage charges over time, especially for large files. If you are done with your project, I recommend cleaning up large files or deleting the bucket entirely to save on storage costs.



Pipeline Quirks
----------------
I wrote this script to take minimal information on variant position (CHROM, POS, REF, ALT) and use the `modules/fake_vcf.py` function to write a full VCF with the minimum set of columns that many informatics programs expects a VCF to have ('CHROM', 'POS', 'ID','REF','ALT','QUAL','FILTER','INFO','FORMAT'). I find this useful for simulating variants in situations where I do not care about things such as variant phase, genotype, or read quality.

Depending on the type of Dataproc instrance that you provision, this annotation code may run slowly. A test run of this script with ??? variants using the default instance initiated by the `hailctl` module took ~10 hours to completion.

ANNOTATION also filters to AF < 0.1.


