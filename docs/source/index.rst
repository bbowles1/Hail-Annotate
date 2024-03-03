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

During my PhD, I frequently needed to annotate VCF files with allele frequency information from GnomAD. For this task, I used a locally-downloaded version of the GnomAD v2.1.1 exome and genome VCF files which I stored on an external 2TB hard drive. Writing Hail code to accomplish this was fairly straightforward, but annotating large VCF files was troublesome and occasionally exceeded the available space on my external hard drive (in addition to being very slow to run). For this reason, I developed a simple pipeline which uses Google Cloud to run Hail Annotation tasks.

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
3. Either make it clear that I am hard-filtering to rare variants, or provide an input parameter that allows user to customize this param.
4. This repo is really intended to simplify the dataproc side of things for a beginner Hail user. I could make this more clear in my documentation if I wanted. Most of the customization is wrapped up in the config JSON step.