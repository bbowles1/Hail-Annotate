Launching Computing Tasks
==========================

Installing Hail
---------------

Hail provides a wrapper for Google Dataproc, ``hailctl``. The ``hailctl`` command provisions Dataproc clusters which already contain installations of the Hail library. This saves us the trouble of setting up Hail on our own Dataproc clusters, although we will still need Hail on our local computer to initiate such instances. Users can install Hail using their favorite package manager (I have used both pip and conda). More detailed instructions on downloading Hail can be found `here <https://hail.is/#install>`_.


Hail Annotation Scripts
------------------------
This guide makes use of several annotation scripts which are designed to take input VCF information and annotate them with GnomAD information. I am specificially interested in annotating input VCF files with information on exome and genome frequency in Hail v2.1.1, although this code is readily adaptable to other Hail releases.

The annotation pipeline is very simple, and makes use of the following:

1. An input JSON config to specify annotation parameters and a path for output data.
2. The ``hail_annotation.py`` which contains utilities to parse the input config, execute the annotation task, and upload the output data to your Google Cloud destination.


Pipeline Input
---------------
The input file for this annotation task should ideally conform to the VCF `v4.0 specification <https://www.internationalgenome.org/wiki/Analysis/Variant%20Call%20Format/vcf-variant-call-format-version-40/>`_. At minimum, your input file must be tab-delimited, and must contain the following fields specifying genomic coordinates: CHROM, POS, REF, ALT. 

The CHROM field can can be in either "chrX" or "X" format, but output data will contain the chromosome number alone without the chr- prefix.


Editing Annotation Parameters
-----------------------------
Users will need to edit this repository's ``config.json`` file to specify which versions of Hail exome/genome data they wish to use for annotation. This config will need to be hosted in a Google Cloud bucket to be accessible to the pipeline.

The JSON config has the following fields:

**GnomAD Paths**

1. Exomes: A Google cloud path to the hail table (.ht) directory containing the GnomAD exomes allele frequency data.
2. Genomes: A Google cloud path to the hail table (.ht) directory containing the GnomAD genomic allele frequency data.

**Script Parameters**

1. Testing: If true, the annotation pipeline will subset your data to variants located on chr22. This is useful for testing pipeline functionality on a small set of your data.
2. Allele Frequency Cutoff: A float value between 0 and 1. If you specify an allele frequency cutoff for your data below 1, any variants with allele frequency above (or equal to) this threshold will be filtered from your output.
3. Input VCF: This is a Google Cloud path to your input VCF file. You must copy your data to an appropriate Google Cloud destination. Your path must contain the full ``gs://bucket/input.vcf`` syntax.
4. Output name: This is a Google Cloud path to your output file. Like the input VCF, this must be a full cloud path with the ``gs://bucket/output-name.vcf`` syntax. It should be a file path, not a directory path.


Creating a DataProc Instance
-----------------------------
Now that we've set up our Cloud project, bucket, and service account, we can now start initiating DataProc computing tasks. We can create a Dataproc instance using:

.. code-block:: bash

    hailctl dataproc start gnomad-test \
        --region us-west1 \
        --service-account=test-service-account@your-project.iam.gserviceaccount.com


Launching Annotation Task
-------------------------
We can submit our job to the cluster using:

.. code-block:: bash

    hailctl dataproc submit gnomad-test /local/path/to/hail_annotation.py \ 
        --config gs://hail-annotation-scripts/test_config.json \ 
        --region us-west1

The input ``hail_annotation.py`` should be hosted locally, but your input config should be hosted in a Google Cloud bucket (ideally the same bucket as your input VCF). The dataproc will save an output file to HDFS storage and then copy it to Google Cloud.


Cleaning Up
-------------
1. The below command stops your dataproc instance:

.. code-block:: bash

    hailctl dataproc stop gnomad-test --region us-west1

2. Confirm that your instance is no longer running using the below commands:

.. code-block:: bash

    gcloud dataproc clusters list --region=us-west1
    
    gcloud compute instances list --region=us-west1

3. Clean up Google Cloud Bucket (*optional*).

Your Google Cloud bucket will accumulate storage charges over time, especially for large files. If you are done with your project, I recommend cleaning up large files or deleting the bucket entirely to save on storage costs.


Example JSON
-------------

Below is a full example JSON config.

.. code-block:: python

    {"gnomad-paths" :
        {
            "exomes": {
                "value" : "gs://gcp-public-data--gnomad/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht/",
                "type" : "google-cloud-path"
            },
            "genomes": {
                "value" : "gs://gcp-public-data--gnomad/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht/",
                "type" : "google-cloud-path"
            }
        },
    "script-params" : 
        {
            "testing" : {
                "value": false,
                "type" : "boolean"
            },
            "allele-frequency-cutoff" : {
                "value" : 0.1,
                "type" : "float"
            },
            "input-vcf" : {
                "value" : "gs://bucket-name/input.vcf",
                "type" : "google-cloud-path"
            },
            "output-name" : {
                "value" : "gs://bucket-name/input.annotated.vcf",
                "type" : "google-cloud-path"
            }
        }
    }


