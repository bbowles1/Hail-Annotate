.. Hail-Annotate documentation master file, created by
   sphinx-quickstart on Sat Jan 27 15:34:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Hail-Annotate's documentation!
=========================================

**Hail-Annotate** is a Python-based guide that helps users annotate genetic variant information 
with allele frequencies from the GnomAD population genomics database. This project is not affilitated with the GnomAD or Hail teams, although users can familiarize themselves with GnomAD 
via the project's `official website <https://gnomad.broadinstitute.org/>`_. 

The following pages will walk users through a small project to take a variant call format (VCF) file and 
annotate the variants with their corresponding allele frequencies in the GnomAD dataset.

This library will require the use of the `Hail genomics library <https://hail.is/>`_ and Google Cloud infrastructure. 
Please refer to the "Getting Started" section for full details.

Project Motivation
-------------------

I often need to annotate VCF files with allele frequency information from GnomAD. For my annotation tasks, I initially used a locally-downloaded version of the GnomAD v2.1.1 exome and genome VCF files which I stored on an external hard drive. Writing Hail code to accomplish this was fairly straightforward, but annotating large VCF files was troublesome and occasionally exceeded the available space on my external hard drive (in addition to being very slow to run). For this reason, I developed a simple pipeline which uses Google Cloud to run Hail Annotation tasks. While I think Hail is very well documented, I struggled to write Hail code and deploy it on Google Cloud. I created this repository in the hopes of guiding others through this process.

Acknowledgements
-----------------

Many thanks to the Hail team, especially Dan King, who's own `Hail Cloud tutorials <https://github.com/danking/hail-cloud-docs>`_ were of considerable help as I developed this project.

.. note::

   This project is under active development and is not associated with the Broad Institute, the Hail team, or the GnomAD project. This work is something that I have undertaken in my free time and it is not affiliated with any of my past or present employers.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   Overview <overview>
   Google Cloud Setup <google_setup>
   Launching Annotation <launching_annotation>


TDL
==================
3. Either make it clear that I am hard-filtering to rare variants, or provide an input parameter that allows user to customize this param.

4. Add notes on input VCF:
Must be .tsv and have chrom, ref, pos, alt columns as a minimum


Here's a good example of the type of input I should aim for:
gcloud dataproc jobs submit pyspark \
    --cluster=my-dataproc-cluster \
    --region=my-region \
    --py-files=gs://path-to/annotation.py \
    --files=gs://path-to/input.vcf,gs://path-to/config.json \
    gs://path-to/annotation.py


Additional features
This module could also use logging support
I notice that the output is keyed by variant when I would prefer it be keyed by original VCF columns - test w/ current gnomad-test.vcf