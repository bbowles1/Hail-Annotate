Overview
=================

What is GnomAD?
----------------

The GnomAD database is a foundational resource in the genetics field which provides information on variant allele frequency and gene constraint. It is a database of healthy individuals who have received exome or genome sequencing. As of release v4.0, the GnomAD database contains information from over 800,000 individuals. The fundamental premise of the GnomAD database is that regions of the genome which have critical biological functions will exhibit fewer mutations in healthy human populations. 


Case Study for GnomAD Usage
----------


A common use case for the GnomAD dataset in clinical genomics is to identify benign mutations in a sequencing report. For example, the *CFTR* gene is a cause of autosomal recessive Cystic Fibrosis. Say you are a clinician and, in the process of screening your patient for disease-causing mutations, you observe an Adenine to Guanine variant on Chromosome 7, position 117480192, which occurs within an intron of *CFTR* (this can be represented as a 7-117480192-A-G variant in GnomAD GRCh38 coordinates). This exact variant has been observed 231 times in healthy GnomAD individuals and has an allele frequency of 0.0001458 across all individuals in the database. Furthermore, there are two individuals who were observed with homozygous mutations in this gene. Further investigation is needed to conclusively rule out this variant as a cause of disease, but the weight of the evidence from GnomAD suggests that this change is not a major driver of cystic fibrosis. 

While this example is only one of the many ways the GnomAD database provides useful information for clinicians and researchers, it is emblematic of a foundational clinical genetics task: matching patient genetic variants to the wealth of information available in GnomAD.


What are VCF Files?
-------------------

Sequencing a biological sample generates a great deal of information in the form of raw reads, which are then aligned to a reference genome. Differences between the sample genome and the reference genome are considered variant positions, and information on these variants is stored in `variant call format (VCF) files <https://www.internationalgenome.org/wiki/Analysis/Variant%20Call%20Format/vcf-variant-call-format-version-40/>`_. 

The identity of a genetic variant is represented by the following set of columns in a VCF file:
- CHROM: The chromosome the variant occurs on, such as "X" or "chrX"
- POS: The integer position on the chromosome that the variant occurs in.
- REF: The reference allele (A, C, T, or G) at the site.
- ALT: The alternate allele, or variant allele, at the site.

VCF files can contain other information, such as phase information, depending on the alignment pipline used to generate them. However, the CHROM, REF, POS, and ALT columns provide the core coordinate info within VCF files.

If we want to obtain allele frequency information for variants in a VCF file, we can match them to variants in the GnomAD database using information from the CHROM, POS, REF, and ALT columns. We can do this ourselves for single variants: for example, our CFTR variant from the "What is GnomAD" section can be represented as 7-117480192-A-G and we can search for it directly on the GnomAD website. But say you have a clinical pipeline where you must scalably annotate allele frequency information for thousands of individuals. How can you go about this? Fortunately, the GnomAD team has published a tool called `Hail <https://hail.is/>_` which is designed to scale this annotation process for very large datasets.

Why use Hail?
--------------

The Hail team has done a great job of `documenting their tools <https://hail.is/>`_ and making a case for why you should use their library. To summarize their goals, they want to make annotating your very large genomic datasets A) memory efficient and B) deployable within cloud infrastructure. They also have made very slick interfaces for running common population genomics analyses - Hail provides an easy interface for you to perform common population genomics tasks such as removing related individuals from a dataset or fitting a linear regression to genotype/phenotype data. Don't be intimidated by the library: users with a basic familiarity of Python (especially the Pandas library) will find Hail to be fairly intuitive. Furthermore, the Hail documentation is excellent and provides many resources for users wishing to learn Hail.

Why Google Cloud?
-----------------
The Hail team has taken great care to make their library work well within the Google Cloud computation environment. For computation tasks involving very many individuals, where the computing requirements would exceed those provided by a single computer, Google cloud provides a scalable solution with many times more computing power. Furthermore, all Hail datasets are currently `hosted on the Google cloud. <gs://gcp-public-data--gnomad>`_, which means you do not have to manually download and host the many gigabytyes of Hail data that you may require for a project.

