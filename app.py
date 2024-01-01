#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script syntax:

Expected config structure:

"""

import json
import pandas as pd
import os, shutil
import hail_annotation as ha
import argparse

def open_config(config_path):

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
        raise Exception(f"Input config is missing the following keys: {missing}")

    types_check = [type(config[i]) == dtypes[i] for i in config.keys()]
    if not all(types_check):
        improper = [i for i in config.keys() if type(config[i]) != dtypes[i]]
        for value in improper:
            print(f"{value} had unexpected type. Expected type {dtypes[value]}, \
                received type {type(config[value])}.")
        raise Exception("Improper config data types!")
    
    return config
        
def main(input_path, output_path, config_path):

    # import config
    config = open_config(config_path)
    print("Imported config!")

    # read VCF as pandas df
    vcf = pd.read_csv(input_path, sep='\t')

    # run annotation script
    ha.hail_annotate(vcf, output_path, config)

    # cleanup all files in cache
    # remove all files in config['cache']


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

    main(args.input, args.output, args.config)