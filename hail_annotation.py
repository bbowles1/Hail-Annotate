#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 09:13:35 2023

@author: bbowles1
"""

from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden
import json
import re
import os

import hail as hl
import pandas as pd
import numpy as np
import subprocess
import argparse

# ====================================== #
#    ____ ___  _   _ _____ ___ ____      #
#   / ___/ _ \| \ | |  ___|_ _/ ___|     #
#  | |  | | | |  \| | |_   | | |  _      #
#  | |__| |_| | |\  |  _|  | | |_| |     # 
#   \____\___/|_| \_|_|   |___\____|     #
#                                        #
# ====================================== #


def parse_gcs_path(gcs_path):
    """Get bucket and blob from a GCS path

    :param gcs_path: GCS path with gs://bucket/blob.file format
    :type gcs_path: str
    :return: tuple with bucket, blob paths as strings
    :rtype: tuple
    """    
    gcs_path  = gcs_path.replace('gs://','')
    bucket = os.path.dirname(gcs_path)
    blob = os.path.basename(gcs_path)
    return bucket, blob


def is_valid_gcs_path(gcs_path):
    """Check that input string is a valid gcs_path

    :param gcs_path: String path to gcs file.
    :type gcs_path: str
    :return: True if string is a valid gcs_path
    :rtype: bool
    """    
    pattern = r'^gs://[a-zA-Z0-9.\-_]{1,255}/.*$'
    return re.match(pattern, gcs_path) is not None


def check_bucket_exists(bucket_name):
    """Check if a GCS bucket exists.

    :param bucket_name: Name of target bucket with "bucket-name" format (no gs:// prefix)
    :type bucket_name: str
    :return: True if bucket exists
    :rtype: bool
    """

    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
        return True
    except NotFound:
        return False


def check_bucket_permission(bucket_name):
    """Check if current account has permission to read bucket

    :param bucket_name: Name of target bucket with "bucket-name" format (no gs:// prefix)
    :type bucket_name: str
    :return: True if bucket exists
    :rtype: bool
    """

    storage_client = storage.Client()
    try:
        bucket = storage_client.get_bucket(bucket_name)
        # Attempt to list blobs in the bucket to check permission
        blobs = list(bucket.list_blobs())
        return True
    except Forbidden:
        return False


def check_gcs_path(gcs_path):
    """Check if a gs bucket exists and you have permission to access it

    :param gcs_path: gcs_path to bucket (gs://path-to-bucket/)
    :type gcs_path: str
    """

    bucket_name, _ = parse_gcs_path(gcs_path)
    exists = check_bucket_exists(bucket_name)
    has_permission = check_bucket_permission(bucket_name)
    if not exists:
        raise Exception("Cannot locate input config bucket!")
    if not has_permission:
        raise Exception("This service account does not have permission to read your input bucket!")

    return exists, has_permission


def load_config(gcs_path):
    """Read input config for a Hail annotation project.

    :param gcs_path: Path to Google Cloud config.json file
    :type gcs_path: str
    """

    # parse bucket/blob format
    bucket, blob = parse_gcs_path(gcs_path)

    # connect to bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(blob)

    # read json
    with blob.open("r") as f:
        config = json.load(f)

    return config


def check_fields(config):
    """Check that the input config has all expected fields.

    :param config: Imported config file.
    :type config: dict
    :raises Exception: Main level of json is missing keys.
    :raises Exception: GnomAD Paths are missing from input json.
    :raises Exception: Script parameters are missing from input json.
    """    
    
    # define expected fields
    level1_keys = ['gnomad-paths','script-params']
    gnomad_keys = ['exomes','genomes']
    script_params = ['testing', 'allele-frequency-cutoff', 'input-vcf', 'output-name']

    missing_keys = [i for i in level1_keys if i not in config.keys()]
    if missing_keys:
        except_str = f"The following keys are missing from first level of your config: {', '.join(missing_keys)}."
        raise Exception(except_str)
        
        
    missing_keys = [i for i in gnomad_keys if i not in config['gnomad-paths'].keys()]
    if missing_keys:
        except_str = f"The following keys are missing from the 'gnomad_keys' level of your config: {', '.join(missing_keys)}."
        raise Exception(except_str)  
        
        
    missing_keys = [i for i in script_params if i not in config['script-params'].keys()]
    if missing_keys:
        except_str = f"The following keys are missing from the 'script-params' level of your config: {', '.join(missing_keys)}."
        raise Exception(except_str)   



def check_types(configvalue, configtype):
    """Check that config types conform to expected values.

    :param configvalue: 'value' field of config leaf node.
    :type configvalue: object (variable type)
    :param configtype: Expected type of config ('google-cloud-path','float','boolean','hdfs-path')
    :type configtype: str
    :raises Exception: Invalid 'type' field was provided.
    :raises Exception: Invalid gcs_path was provided.
    :raises Exception: Input config value must be a float.
    :raises Exception: Input config value must be a boolean.
    :raises Exception: Input config value must be a string.
    """    
    types = ['google-cloud-path','float','boolean', 'string']
    
    if configtype not in types:
        raise Exception(f"Type {configtype} is invalid! Expecting values in: {types}.")
        
    if configtype == 'google-cloud-path':
        if not is_valid_gcs_path(configvalue):
            raise Exception(f"Input path {configvalue} is not a valid GCS path!")
            
    if configtype == 'float':
        if not isinstance(configvalue, float):
            raise Exception(f"Input config value {configvalue} must be a float!")
            
    if configtype == 'boolean':
        if not isinstance(configvalue, bool):
            raise Exception(f"Input config value {configvalue} must be True or False!")
        
    if configtype == 'string':
        if not isinstance(configvalue, str):
            raise Exception(f"Input config value {configvalue} must be string!")

def check_config_types(config):
    """Check input config for expected data types.

    :param config: Loaded config.json file.
    :type config: dict
    """    

    # loop over config structure
    for level1key in config.keys():
        for level2key in config[level1key].keys():
            if 'type' in config[level1key][level2key].keys():

                # extract value, type
                configvalue = config[level1key][level2key]['value']
                configtype = config[level1key][level2key]['type']
                # check that value is expected type
                check_types(configvalue, configtype)

     
def import_config(gcs_path):
    """Main function of this file. Wraps basic type, permission
    checks on input path, then loads the config.

    :param gcs_path: Input path to a config.json on Google Cloud.
    :type gcs_path: str
    :raises Exception: Input path is not a valid GCS path.
    :raises Exception: Cannot open GCS path (either does not exist or you do not have permission)
    :return: loaded config
    :rtype: dict
    """    

    # check that google cloud path is valid
    if not is_valid_gcs_path:
        raise Exception("Invalid GCS-path to config!")
    exists, has_permissions = check_gcs_path(gcs_path)
    if not all([exists, has_permissions]):
        raise Exception(f"Cannot open GCS-path. Bucket exists/is visible: {exists}. Account has permissions to read bucket: {has_permissions}.")
    
    # read config
    print(f'Loading config from {gcs_path}')
    config = load_config(gcs_path)

    # check that config fields are expected
    check_fields(config)

    # Check that config types are expected.
    check_config_types(config)

    return config


# =============================== #               
#   _   _    _    ___ _           #
#  | | | |  / \  |_ _| |          #
#  | |_| | / _ \  | || |          #
#  |  _  |/ ___ \ | || |___       #
#  |_| |_/_/   \_\___|_____|      #
#                                 #
# ================================#

def read_vcf(path):
    """Import VCF with support for CHROM or #CHROM header

    :param path: GCP path to VCF
    :type path: str
    :return: Imported VCF
    :rtype: pd.DataFrame
    """

    # read header
    df = pd.read_csv(path,
                     sep='\t',
                     nrows=2000,
                     header=None)
    
    # parse for #CHROM field
    for row in df.itertuples():
        if any(['#CHROM' in str(i) for i in row[1:]]):
            cols = list(row)[1:]
            hash_header=True
            break
        if any(['CHROM' in str(i) for i in row[1:]]):
            cols = list(row)[1:]
            hash_header=False
            break

    # import full VCF
    df = pd.read_csv(path,
                     sep='\t',
                     comment='#',
                     header=None,
                     names=cols)
    
    # cut duplicate header fields
    if hash_header == False:
        df = df.iloc[1:]
    
    return df



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


def fake_vcf(input_df,
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
    
    # use HDFS for output
    output_dir = 'hdfs:///tmp/'

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
    command = f"hdfs dfs -cat {output_path.replace('hdfs://','')} | sed -e '1i\##fileformat=VCFv4.2' | hadoop fs -put -f - {newfile.replace('hdfs://','')}"
    print(command)
    subprocess.check_output(command, shell=True)

    # clean up tmp file from HDFS
    command = f"hdfs dfs -rm -R {output_path.replace('hdfs://','')}"
    print(command)
    subprocess.check_output(command, shell=True)
    
    # return output path for reference
    return(newfile)
    

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

    # set af cutoff for exome and genome frequency (all subpopulations)
    af_cutoff = config['script-params']['allele-frequency-cutoff']['value']
                        
    if db == "exomes":
        # annotate VCF with exome information
        ht = hl.read_table(config['gnomad-paths']['exomes']['value'])
        #logger.debug(f"BRADLOG: Annotating DB type: {db}. Input rows: {vcf.count()}.")
        vcf = vcf.annotate_rows(efreq=ht[vcf.locus, vcf.alleles].freq.AF[0])
        #logger.debug(f"BRADLOG: Annotated rows with 'efreq' field. Output rows: {vcf.count()}.")
        vcf = vcf.annotate_rows(epopmax=ht[vcf.locus, vcf.alleles].popmax.AF[0])
        #logger.debug(f"BRADLOG: Annotated rows with 'epopmax' field. Output rows: {vcf.count()}.")
        
        # fill missing values in efreq, epopmax columns
        vcf = vcf.annotate_entries(
            efreq_filled = hl.if_else(
                hl.is_missing(vcf.efreq),
                0.0,
                vcf.efreq
            ),
            epopmax_filled = hl.if_else(
                hl.is_missing(vcf.epopmax),
                0.0,
                vcf.epopmax
            )
        )

        # drop and rename columns
        vcf = vcf.drop('efreq', 'epopmax')
        vcf = vcf.rename({'efreq_filled': 'efreq', 'epopmax_filled': 'epopmax'})

        # use hail aggregators to filter for variants below AF cutoff
        vcf = vcf.filter_rows(
            hl.agg.count_where(vcf.efreq < af_cutoff) > 0)
        #logger.debug(f"BRADLOG: Filtering on allele frequency using 'efreq' field. Output rows: {vcf.count()}.")
        
    if db == "genomes":
        
        # annotate vcf with genome information
        ht = hl.read_table(config['gnomad-paths']['genomes']['value'])
        #logger.debug(f"BRADLOG: Annotating DB type: {db}. Input rows: {vcf.count()}.")
        vcf = vcf.annotate_rows(gfreq=ht[vcf.locus, vcf.alleles].freq.AF[0])
        #logger.debug(f"BRADLOG: Annotated rows with 'gfreq' field. Output rows: {vcf.count()}.")
        vcf = vcf.annotate_rows(gpopmax=ht[vcf.locus, vcf.alleles].popmax.AF[0])
        #logger.debug(f"BRADLOG: Annotated rows with 'gpopmax' field. Output rows: {vcf.count()}.")

        # fill missing values in efreq, epopmax columns
        vcf = vcf.annotate_entries(
            gfreq_filled = hl.if_else(
                hl.is_missing(vcf.gfreq),
                0.0,
                vcf.gfreq
            ),
            gpopmax_filled = hl.if_else(
                hl.is_missing(vcf.gpopmax),
                0.0,
                vcf.gpopmax
            )
        )

        # drop and rename columns
        vcf = vcf.drop('gfreq', 'gpopmax')
        vcf = vcf.rename({'gfreq_filled': 'gfreq', 'gpopmax_filled': 'gpopmax'})

        # use hail aggregators to filter for variants below AF cutoff
        vcf = vcf.filter_rows(
            hl.agg.count_where(vcf.gfreq < af_cutoff) > 0)
        #logger.debug(f"BRADLOG: Filtering on allele frequency using 'gfreq' field. Output rows: {vcf.count()}.")

    if db == "proportion_expressed":
        
        # annotate with proportion expressed
        ht = hl.read_table(config['gnomad-paths']['proportion_expressed']['path'])
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
    hdfs_path = fake_vcf(input_df[["CHROM","POS","REF","ALT"]], use_chr=False)
        
    # read matrix table
    vcf = hl.import_vcf(hdfs_path)
    
    # split mutliallelic entries
    vcf = hl.split_multi(vcf)
    # NOTE THAT THIS HANDLES the `GT` FIELD ODDLY, SEE DOCS
    # https://hail.is/docs/0.2/methods/genetics.html#hail.methods.split_multi

    # if testing, create smaller variant subset
    if config['script-params']['testing']['value']:
        vcf = vcf.filter_rows(vcf.locus.contig == '22')

    return vcf


def hail_annotate(input_df, config):
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
    
    # export table to HDFS storage
    export = vcf.select_entries(vcf.efreq, vcf.epopmax, vcf.gfreq, vcf.gpopmax).entries()
    output_path = 'hdfs:///tmp/hail-annotate-output.tsv'
    export.export(output_path)
    print(f"Wrote annotated VCF to {output_path}.")


def execute_annotation(config_path):
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
    config = import_config(config_path)
    print("Imported config.")

    # read VCF as pandas df
    vcf = read_vcf(config['script-params']['input-vcf']['value'])

    # run annotation script
    hail_annotate(vcf, config)

    # upload to GCP
    destination_path = config['script-params']['output-name']['value']
    upload_to_cloud(destination_path
                    )

    print(f"Run completed. Annotated file written to {destination_path}")


def upload_to_cloud(destination_path):
    """Upload annotated file to Google Cloud. Requires "Storage Folder Admin" permission.

    :param destination_path: GCP Destination path parsed from Config
    :type destination_path: str
    """

    # perform efficient Hadoop-style Upload
    command = f"hadoop distcp hdfs:///tmp/hail-annotate-output.vcf {destination_path}"
    print(command)
    subprocess.check_output(command, shell=True)

    print(f"Annotated output loaded to {destination_path}.")



# =============================== #
#   __  __          _____ _   _   #
#  |  \/  |   /\   |_   _| \ | |  #
#  | \  / |  /  \    | | |  \| |  #
#  | |\/| | / /\ \   | | | . ` |  #
#  | |  | |/ ____ \ _| |_| |\  |  #
#  |_|  |_/_/    \_\_____|_| \_|  #
#                                 #
# =============================== #


if __name__ == '__main__':

    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Use cloud infrastructure to \
                                     add Hail annotations to an input VCF file.')
    
    # Get arguments
    parser.add_argument('--config', type=str,
                        help='GCP path to a config with annotation parameters.')
    args = parser.parse_args()

    # execute main
    execute_annotation(args.config)
