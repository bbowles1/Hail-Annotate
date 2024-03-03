#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 09:13:35 2023

@author: bbowles
"""

import hail as hl
import os
import pandas as pd
import numpy as np
import json
import subprocess
import argparse

def open_config(config_path):
    """This function is designed to parse an input JSON for 
    parameters needed to execute a GnomAD annotation task.

    :param config_path: Path to config.json file within a Google DataProc instance.
    :type config_path: str
    :raises ValueError: Input config is missing required keys.
    :raises ValueError: Config keys contain improper data types.       
    :return: 
        Dictionary of parsed JSON keys defining annotation workflow parameters.
    :rtype: dict
    """

    # read json config
    with open(config_path) as f:
        config = json.load(f)

    # check for all required keys, dtypes
    dtypes = {'exomes':dict,
            'genomes':dict,
            'cache':dict,
            'testing':bool}

    keys_check = [i in config.keys() for i in dtypes.keys()]
    if not all (keys_check):
        missing = [i for i in dtypes.keys() if i not in config.keys()]
        raise ValueError(f"Input config is missing the following keys: {missing}")

    types_check = [type(config[i]) == dtypes[i] for i in config.keys()]
    if not all(types_check):
        improper = [i for i in config.keys() if type(config[i]) != dtypes[i]]
        for value in improper:
            print(f"{value} had unexpected type. Expected type {dtypes[value]}, \
                received type {type(config[value])}.")
        raise ValueError("Improper config data types!")
    
    return config


def fake_vcf(input_df, 
             output_dir,
             use_chr=True):
    """Spoof a VCF file structure when passed an input DataFrame containing CHROM, REF, POS, ALT columns. 
    For all columns in 'ID', 'QUAL', 'FILTER', 'INFO', 'FORMAT', adds any columns which are not present.
    Added columns will be contain empty data. This script will overwrite any existing information in the 
    VCF header, ie contig information.

    :param input_df: Pandas DataFrame with 'CHROM', 'REF', 'POS', 'ALT' columns.
    :type input_df: pd.DataFrame

    :param output_dir: Output directory to write VCF to.
    :type output_dir: str

    :param use_chr: If True, appends a 'chr' prefic to all CHROM entries if not already present.
    :type use_chr: bool

    :raises pd.errors.ParserError: Input DataFrame is missing required columns.
    :raises pd.errors.ParserError: Required input columns contain missing data.
    """    
    
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
    
    # copy newfile to hdfs
    hdfs_path = 'hdfs:///tmp/fake_vcf.vcf'
    subprocess.run(['hadoop', 'dfs', '-put', '-f', newfile, 'hdfs:///tmp/'], check=True)

    # return output path for reference
    return(hdfs_path)


def is_vcf(input_df):
    """Return True if input contains minimum VCF columns
    (CHROM, POS, REF, ALT).

    :return: True if VCF file contains minimum required headers.
    :rtype: bool
    """    
    
    # VCF cols are missing
    if not all([i in input_df.columns for i in ["CHROM","POS","REF","ALT"]]):
        return False
        
    else:
        return True
    

def add_db_annotations(vcf, db, config):
    """Annotates input VCF with GnomAD data specified by the 
    `db` parameter.

    :param vcf: VCF file, which has been given all required keys and converted to a Hail table.
    :type vcf: hail.Table

    :param db: Key matching a GnomAD database listed within the config.json, either "exomes" or "genomes."
    :type db: str

    :param config: path to config.json containing GnomAD database cloud bucket paths.
    :type config: str

    :return: Hail Table annotated with 
    :rtype: hail.Table
    """    
                        
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
        
    return vcf

    
def vcf_to_mt(input_df, config):
    """Converts an input VCF with minimum required columns 
    (CHROM, POS, REF, ALT) to a Hail table.

    :param input_df: Pandas dataframe with minimal required VCF columns
    :type input_df: pd.DataFrame

    :param config: Path to config containing tmp directory to use for caching VCF file.
    :type config: str

    :return: VCF converted to hail.Table (function name is a misnomer)
    :rtype: hail.Table
    """

    # check if VCF cols are present in input df
    hdfs_path = fake_vcf(input_df[["CHROM","POS","REF","ALT"]], 
                    output_dir=config['cache']['path'], use_chr=False)
    
    # download from hdfs storage to dataproc worker node
    local_path = '/tmp/fake_vcf.vcf'
    subprocess.run(['hadoop', 'dfs', '-get', '-f', hdfs_path, local_path], check=True)
    

    # convert input to matrix table
    #matrixpath = os.path.join(config['cache']['path'], "hail_temp_matrix_table.tmp.mt")
    #hl.import_vcf(local_path).write(matrixpath, overwrite=True)
    
    # read matrix table
    #vcf = hl.read_matrix_table(matrixpath)
    vcf = hl.import_vcf(local_path)
    
    # split mutliallelic entries
    vcf = hl.split_multi(vcf)
    # NOTE THAT THIS HANDLES GT INFORMATION ODDLY, SEE DOCS
    # https://hail.is/docs/0.2/methods/genetics.html#hail.methods.split_multi

    # if testing, create smaller variant subset
    if config['testing']:
        vcf = vcf.filter_rows(vcf.locus.contig == '22')

    return vcf


def hail_annotate(input_df, output_path, config):
    """Runs Hail annotation scripts for all input GnomAD databases.

    :param input_df: Pandas Dataframe containing minimum required VCF columns (CHROM, POS, REF, ALT)
    :type input_df: pd.DataFrame

    :param output_path: Output path on DataProc instance to use for writing annotated data. 
    Output data contains epopmax, gpopmax, and proportion_expressed,
    keyed by variant. Allele frequency > 0.01 is returned as NA.
    :type output_path: str

    :param config: Path to config JSON file containing workflow parameters.
    :type config: str
    """    
            
    vcf = vcf_to_mt(input_df, config)

    for db in ['exomes','genomes']:
        
        print(f"Adding annotations for: {db}")
        vcf = add_db_annotations(vcf, db, config)
        print(f"Done with annotations for: {db}")

    # construct a variant expression
    vcf = vcf.annotate_rows(variant=vcf.locus.contig + ':' + hl.format('%s', vcf.locus.position) + vcf.alleles[0] + '>' + vcf.alleles[1])
    
    # key by variant expression, drop other keys
    vcf = vcf.key_rows_by(vcf.variant)
    
    # export table
    export = vcf.select_rows(vcf.efreq, vcf.epopmax, vcf.gfreq, vcf.gpopmax).rows()
    export.export(output_path)
    print(f"Wrote annotated VCF to {output_path}.")


def main(input_path, output_path, config_path):
    """Wrapper which opens config path, reads input VCF, 
    and launches annotation script.

    :param input_path: Path (on DataProc instance) to input, tab-delimited file with CHROM, POS, REF, ALT columns.
    :type input_path: str

    :param output_path: Output path (on DataProc instance) to use for writing output, annotated data.
    :type output_path: str

    :param config_path: Path (on DataProc instance) to config JSON file containing workflow parameters.
    :type config_path: str
    """

    # import config
    config = open_config(config_path)
    print("Imported config!")

    # read VCF as pandas df
    vcf = pd.read_csv(input_path, sep='\t')

    # run annotation script
    hail_annotate(vcf, output_path, config)

    # cleanup all files in cache
    # remove all files in config['cache']

    print(f"Run completed. Annotated file written to {output_path}")


if __name__ == '__main__':

    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Use cloud infrastructure to \
                                     add Hail annotations to an input VCF file.')
    
    # Get arguments
    parser.add_argument('--input', type=str,
                        help='Input VCF file with minimum required fields CHROM, POS, REF, ALT.')
    parser.add_argument('--output', type=str,
                        help='Output path for tab-delimited file.')
    parser.add_argument('--config', type=str,
                        help='Config with annotation parameters.')
    args = parser.parse_args()

    # execute main
    main(args.input, args.output, args.config)
