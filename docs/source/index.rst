.. Hail-Annotate documentation master file, created by
   sphinx-quickstart on Sat Jan 27 15:34:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Hail-Annotate's documentation!
=========================================

**Hail-Annotate** is a Python-based guide that helps users annotate genetic variant information 
with allele frequencies from the GnomAD population genomics database. Users can familiarize themselves with GnomAD 
via this project's `official website <https://gnomad.broadinstitute.org/>`_. 

The following pages in this documentation will walk users through a small project to take a variant call format (VCF) file and 
annotate the variants within with their corresponding allele frequencies in the GnomAD dataset.

This library will require the use of the `Hail genomics library <https://hail.is/>`_ and Google Cloud infrastructure. 
Please refer to the "Getting Started" section for full details.

Project Motivation
-------------------

During my PhD, I frequently needed to annotate VCF files with allele frequency information from GnomAD. For this task, I used a locally-downloaded version of the GnomAD v2.1.1 exome and genome VCF files which I stored on an external 2TB hard drive. Writing Hail code to accomplish this was fairly straightforward, but annotating large VCF files was troublesome and occasionally exceeded the available space on my external hard drive (in addition to being very slow to run). For this reason, I developed a simple pipeline which uses Google Cloud to run Hail Annotation tasks. While I think Hail is very well documented, I struggled to write Hail code that I deployed on Google Cloud and created this repository in the hopes of guiding others through this process.

Acknowledgements
-----------------

Many thanks to the Hail team, especially Dan King, who's own `Hail Cloud tutorials <https://github.com/danking/hail-cloud-docs>`_ were of considerable help as I developed this project.

.. note::

   This project is under active development and is not associated with the Broad Institute or the Hail team.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Overview <overview>
   Google Cloud Setup <google_setup>
   Launching Annotation <launching_annotation>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


TDL
==================
1. Move the following definitions from wrapper.py (hard-coded) to the config:
   - input_vcf
   - output_path
   - source bucket
   - make wrapper use "destination_path" within config.
   ^ make these happen and then rework the docstrings.
2. Rework `execute_script` within wrapper.py to be more flexible with syntax.
   - Ideally I want to read the input config directly from Google Cloud, which means I probably need a test script.
3. Either make it clear that I am hard-filtering to rare variants, or provide an input parameter that allows user to customize this param.
4. The config is getting messy because I am providing Google Cloud Paths in addition to local dataproc paths. 
I may want to, for example, add config details that specify the path type.

Add notes on input VCF:
Must be .tsv and have chrom, ref, pos, alt columns as a minimum

Hard-code the following values:
1. cache
2. hdfs output path

Technically, I can provide the config AND the wrapper script locally

I can merge Hail annotation and my wrapper
Becaise I am using large files as input to the Google dataproc instance, I probably need to make sure that the VCF is hosted on Google cloud. The initiation script and the config can both be hosted locally.

Here's a good example of the type of input I should aim for:
gcloud dataproc jobs submit pyspark \
    --cluster=my-dataproc-cluster \
    --region=my-region \
    --py-files=gs://path-to/annotation.py \
    --files=gs://path-to/input.vcf,gs://path-to/config.json \
    gs://path-to/annotation.py

I want to provde the following as input params:
- Path to config.json (local or GCS)
- Path to repo (Python script + modules)

Additional features
This module could also use logging support
I notice that the output is keyed by variant when I would prefer it be keyed by original VCF columns