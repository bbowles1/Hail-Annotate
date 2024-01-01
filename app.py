#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script syntax:

Expected config structure:

"""

import pandas as pd
import hail_annotation as ha
import argparse
        
def main(input_path, output_path, config_path):

    # import config
    config = ha.open_config(config_path)
    print("Imported config!")

    # read VCF as pandas df
    vcf = pd.read_csv(input_path, sep='\t')

    # run annotation script
    ha.hail_annotate(vcf, output_path, config)

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