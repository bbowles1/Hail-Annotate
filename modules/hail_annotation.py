#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 09:13:35 2023

@author: bbowles
"""

import hail as hl
import os
import pandas as pd
import json
import shutil


"""
For testing:
mt = mt.filter_rows(mt.locus.contig == '22')
"""

def fake_vcf(input_df, 
             output_dir='/app/tmp/fake_vcf.vcf',
             use_chr=True):
    
    # spoof a VCF when passes a df containing CHROM, REF, POS, ALT
    # requires a tab-delimited input file
    # uses chr# annotation for CHROM field
    # cannot fool programs that check for contigs
    # pass ostype = "mac" or "linux" for different shell commands to insert header
    
    vcfcols = ['CHROM', 'POS', 'ID','REF','ALT'	,'QUAL','FILTER','INFO','FORMAT']
    
    # raise exception if wrong columns are present
    if False in [i in input_df.columns for i in ['CHROM','POS','REF','ALT']]:
        raise pd.errors.ParserError("Input dataframe is missing VCF variant info colums (CHROM, POS, REF, ALT)!")
    
    # raise exception if input columns have missing data
    if input_df[['CHROM','POS','REF','ALT']].isnull().any().any():
        culprits = ', '.join(input_df.columns[input_df.isnull().any()])
        raise pd.errors.ParserError(('columns ' + culprits + ' contain missing data!'))
    
    # convert CHROM column to string
    input_df.loc[:, 'CHROM'] = input_df.CHROM.astype(str)
    
    # format CHROM column
    if use_chr == True:
        input_df.loc[np.logical_not(input_df.CHROM.str.contains('chr')), 'CHROM'] = 'chr' + input_df.CHROM
    else:
        input_df.loc[(input_df.CHROM.str.contains('chr')), 'CHROM'] = input_df.CHROM.str.replace("chr","")
        
    # fill in other required VCF columns
    newcols = [i for i in ['ID', 'QUAL', 'FILTER', 'INFO', 'FORMAT'] if i not in input_df.columns]
    
    # fill NaN in present required columns
    if not bool(newcols) and input_df[vcfcols].isnull().any().any():
        for colname in ['ID', 'QUAL', 'FILTER', 'INFO', 'FORMAT']:
            input_df.loc[:, colname] = input_df[colname].replace(np.nan, '.')
    
    for colname in newcols:
        input_df[colname] = '.'
        
    # set correct QUAL, FILTER cols
    input_df.loc[input_df.QUAL=='.', 'QUAL'] == 100.00
    input_df.loc[input_df.FILTER=='.', 'FILTER'] == 'PASS'
    
    # add example FORMAT and genotype columns
    input_df['FORMAT'] == 'GT'
    input_df['GT1'] = '0/1'
    
    # order columns
    input_df = input_df[['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT','GT1']]
    
    # drop duplicates
    input_df = input_df.drop_duplicates()
    
    # rename header line
    input_df.rename(columns={'CHROM':'#CHROM'}, inplace=True)
    
    # check for missing values
    if input_df.isnull().sum().any():
        print('Missing data in output VCF file!')
    
    # set output path, write file
    output_path = os.path.join(output_dir, "fake_vcf.tmp.vcf")
    input_df.to_csv(output_path, sep='\t', index=False)  

    
    # inject file format info into metadata    
    newfile = output_path.replace('.tmp','')
    command = 'sed -e \'1i\##fileformat=VCFv4.2\' ' + output_path + ' > ' + newfile
    print(command)
    subprocess.check_output(command, shell=True)
    
    # clean up tmp file
    command = 'rm ' + output_path
    print(command)
    subprocess.check_output(command, shell=True)
    
    # reformat output path
    output_path = output_path.replace('.tmp','')
    
    # return output path for reference
    return(output_path)


def is_vcf(input_df):
    
    """
    Return True if input contains minimum VCF columns
    (CHROM, POS, REF, ALT)
    """
    
    # VCF cols are missing
    if not all([i in input_df.columns for i in ["CHROM","POS","REF","ALT"]]):
        return False
        
    else:
        return True
    

def add_db_annotations(vcf, db, config):
                        
    if db == "exomes":
        # annotate VCF with exome information
        ht = hl.read_table(config['exomes']['path'])
        vcf = vcf.annotate_rows(efreq=ht[vcf.locus, vcf.alleles].freq.AF[0])
        vcf = vcf.annotate_rows(epopmax=ht[vcf.locus, vcf.alleles].popmax.AF[0])
        
        # filter to entries with AF < 0.1
        vcf = vcf.filter_rows(vcf.efreq < 0.01, keep=True)
        
    if db == "genomes":
        
        # annotate vcf with genome information
        ht = hl.read_table(config['genomes']['path'])
        vcf = vcf.annotate_rows(gfreq=ht[vcf.locus, vcf.alleles].freq.AF[0])
        vcf = vcf.annotate_rows(gpopmax=ht[vcf.locus, vcf.alleles].popmax.AF[0])
        
        # filter to entries with AF < 0.1
        vcf = vcf.filter_rows(vcf.gfreq < 0.01, keep=True)

    if db == "proportion_expressed":
        
        # annotate with proportion expressed
        ht = hl.read_table(config['proportion_expressed']['path'])
        vcf = vcf.annotate_rows(proportion_expressed=ht[vcf.locus].mean_proportion)

    # cache result
    #vcf.rows().export(os.path.join(config['cache']['path'], "hail_cache.tmp.tsv"))
        
    return vcf

    
def vcf_to_mt(input_df, testing):

    # check if VCF cols are present in input df
    if is_vcf(input_df):
        path = fake_vcf(input_df[["CHROM","POS","REF","ALT"]], use_chr=False)
    else:
        raise Exception("Input data is missing VCF columns!")

    # convert input to matrix table
    matrixpath = os.path.join(config['cache']['path'], "hail_temp_matrix_table.tmp.mt")
    hl.import_vcf(path).write(matrixpath, overwrite=True)
    
    # read matrix table
    vcf = hl.read_matrix_table(matrixpath)
    
    # split mutliallelic entries
    vcf = hl.split_multi(vcf)
    # NOTE THAT THIS HANDLES GT INFORMATION ODDLY, SEE DOCS
    # https://hail.is/docs/0.2/methods/genetics.html#hail.methods.split_multi

    # if testing, create smaller variant subset
    if testing:
        vcf = vcf.filter_rows(vcf.locus.contig == '22')


def hail_annotate(input_df, output_path, config):
    
    """
    Input: 
        input_df: Pandas dataframe containing minimum VCF cols
        config_path: config .json with the structure {"db_name":{"local":"","remote":""},}
            Json must contain keys ["exomes","genomes","proportion_expressed"]
        af_cutoff: float, output will only contains variants with AF < cutoff
    
    Output: Annotated dataframe containing epopmax, gpopmax, and proportion_expressed,
    keyed by variant. Allele frequency > 0.01 is returned as NA.
    """
            
    vcf = vcf_to_mt(input_df, config['testing'])

    for db in ['exomes', 'genomes']:
        
        print(f"Adding annotations for: {db}")
        vcf = add_db_annotations(vcf, db, config)
        print(f"Done with annotations for: {db}")

    # construct a variant expression
    vcf = vcf.annotate_rows(variant=vcf.locus.contig + ':' + hl.format('%s', vcf.locus.position) + vcf.alleles[0] + '>' + vcf.alleles[1])
    
    # key by variant expression, drop other keys
    vcf = vcf.key_rows_by(vcf.variant)
    
    # export table
    export = vcf.select_rows(vcf.efreq, vcf.epopmax, vcf.gfreq, vcf.gpopmax, vcf.proportion_expressed).rows()
    export.export(output_path, delimiter='\t')
    print(f"Wrote annotated VCF to {output_path}")









def hail_annotate(input_df,
                  exomepath = r'/Users/bbowles/Documents/Code/refdata/gnomad/exomes/gnomad.exomes.r2.1.sites.ht',
                  genomepath = r'/Users/bbowles/Documents/Code/refdata/gnomad/genomes/gnomad.genomes.r2.1.sites.ht',
                  transcriptpath = r'/Users/bbowles/Documents/Code/refdata/gnomad/proportion_expressed/all.baselevel.021620.ht',
                  genomes=True,
                  exomes=True,
                  pex=True):
    
    """
    Input: Pandas dataframe containing minimum VCF cols
    
    Output: Annotated dataframe containing epopmax, gpopmax, and proportion_expressed,
    keyed by variant. Allele frequency > 0.01 is returned as NA.
    """
    
     
    # check if VCF cols are present
    if is_vcf(input_df):
        path = fake_vcf(input_df[["CHROM","POS","REF","ALT"]], use_chr=False)
        
    else:
        raise Exception("Input data is missing VCF columns!")

    # convert input to matrix path
    matrixpath = "/Users/bbowles/Documents/Code/refdata/tmp/hail_temp_matrix_table.tmp.mt"
    hl.import_vcf(path).write(matrixpath, overwrite=True)
    
    # read matrix table
    vcf = hl.read_matrix_table(matrixpath)
    
    # split mutliallelic entries
    vcf = hl.split_multi(vcf)
    # NOTE THAT THIS HANDLES GT INFORMATION ODDLY, SEE DOCS
    # https://hail.is/docs/0.2/methods/genetics.html#hail.methods.split_multi
    
    if exomes:
        # annotate VCF with exome information
        exome = hl.read_table(exomepath)
        vcf = vcf.annotate_rows(efreq=exome[vcf.locus, vcf.alleles].freq.AF[0])
        vcf = vcf.annotate_rows(epopmax=exome[vcf.locus, vcf.alleles].popmax.AF[0])
        
        # filter to entries with AF < 0.1
        vcf = vcf.filter_rows(vcf.efreq < 0.01, keep=True)
    
    if genomes:
        # annotate vcf with genome information
        genome = hl.read_table(genomepath)
        vcf = vcf.annotate_rows(gfreq=genome[vcf.locus, vcf.alleles].freq.AF[0])
        vcf = vcf.annotate_rows(gpopmax=genome[vcf.locus, vcf.alleles].popmax.AF[0])
        
        # filter to entries with AF < 0.1
        vcf = vcf.filter_rows(vcf.gfreq < 0.01, keep=True)
    
    if pex:
        # annotate with proportion expressed
        transcript = hl.read_table(transcriptpath)
        vcf = vcf.annotate_rows(proportion_expressed=transcript[vcf.locus].mean_proportion)
    
    
    # construct a variant expression
    vcf = vcf.annotate_rows(variant=vcf.locus.contig + ':' + hl.format('%s', vcf.locus.position) + vcf.alleles[0] + '>' + vcf.alleles[1])
    
    # key by variant expression, drop other keys
    vcf = vcf.key_rows_by(vcf.variant)
    
    # export table
    exportpath = '/Users/bbowles/Documents/Code/refdata/tmp/hail_annotated_data.tmp.tsv'
    
    # make row selections
    if all([exomes,genomes,pex]):
        export = vcf.select_rows(vcf.efreq, vcf.epopmax, vcf.gfreq, vcf.gpopmax, vcf.proportion_expressed).rows()
    elif all([exomes,genomes]):
        export = vcf.select_rows(vcf.efreq, vcf.epopmax, vcf.gfreq, vcf.gpopmax).rows()
    elif all([exomes,pex]):
        export = vcf.select_rows(vcf.efreq, vcf.epopmax, vcf.proportion_expressed).rows()
    elif all([genomes,pex]):
        export = vcf.select_rows(vcf.gfreq, vcf.gpopmax, vcf.proportion_expressed).rows()
    elif genomes:
        export = vcf.select_rows(vcf.gfreq, vcf.gpopmax).rows()
    elif exomes:
        export = vcf.select_rows(vcf.efreq, vcf.epopmax).rows()
    elif pex:
        export = vcf.select_rows(vcf.proportion_expressed).rows()
    
    export.export(exportpath, delimiter='\t')

    # read result
    return (pd.read_csv(exportpath, sep="\t"))