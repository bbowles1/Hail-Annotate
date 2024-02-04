.. Hail-Annotate documentation master file, created by
   sphinx-quickstart on Sat Jan 27 15:34:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Hail-Annotate's documentation!
=========================================

**Hail-Annotate** is a Python library that helps users annotate genetic variant information 
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

Contents
--------

.. toctree::

   overview

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
