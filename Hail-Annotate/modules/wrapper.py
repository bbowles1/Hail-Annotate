#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Wrapper to instantiate an annotation process on your LOCAL computer
Designed to download files to the dataproc instance and kick off anotation task.
1. Copy repo from GCS to local dataproc instance.
"""

import subprocess
import os
import sys
from config_utils import import_config

# copy everything to local /tmp
def download_data(source_bucket):

    # use a /tmp/ file on local dataproc machine
    destination_path = '/tmp/'

    # Run gsutil cp command using subprocess
    subprocess.run(['gsutil', '-m', 'cp', '-r', source_bucket, destination_path], check=True)


def execute_script(config, wrapper_script_path):

    # working directory
    bucket_leaf = config['script-params']['project-bucket']['value'] need something here to get subdir????
    gcs_wd = os.path.join('/tmp', bucket_leaf)

    # python script is at gcs_path[-1] + wrapper.py
    script_path

    # 


    # run main command
    command = [
        'python',
        wrapper_script_path, # this needs to be a GCS path, we can run checks on it
        '--input',
        input_vcf, # this needs to be a GCS path from the config
        '--output',
        output_path, # this needs to be a GCS path from the config
        '--config',
        '/tmp/Hail-Annotate/config.json' # Can I read this config in directly?
    ]

    # Run the command
    subprocess.run(command, check=True)


def upload_data(output_path):

    destination_path = os.path.join('gs://hail-annotation-scripts/Hail-Annotate/', 
                 os.path.basename(output_path))

    # Run gsutil cp command using subprocess
    #subprocess.run(['gsutil', 'cp', '-f', hdfs_file, destination_path], check=True)
    subprocess.run(['hdfs', 'dfs', '-cp', '-f', output_path, destination_path], check=True)
    print(f'File uploaded to {destination_path}')


# =============================== #
#   __  __          _____ _   _   #
#  |  \/  |   /\   |_   _| \ | |  #
#  | \  / |  /  \    | | |  \| |  #
#  | |\/| | / /\ \   | | | . ` |  #
#  | |  | |/ ____ \ _| |_| |\  |  #
#  |_|  |_/_/    \_\_____|_| \_|  #
#                                 #
# =============================== #

# if __name__ == '__main__':

#     # Instantiate the parser
#     parser = argparse.ArgumentParser(description='Use cloud infrastructure to \
#                                      add Hail annotations to an input VCF file.')
    
#     # Get arguments
#     parser.add_argument('--input', type=str,
#                         help='Input VCF file with minimum required fields CHROM, POS, REF, ALT.')
#     parser.add_argument('--output', type=str,
#                         help='Output path for tab-delimited file.')
#     parser.add_argument('--config', type=str,
#                         help='Config with annotation parameters.')
#     args = parser.parse_args()

#     # execute main
#     main(args.input, args.output, args.config)


Parser Goals:
    wrapper_path = hail_annotation.py
    config = ???? (local path or google cloud path)


if __name__ == "__main__":

    # append modules path
    sys.path.append('gs://mypath/')

    # import config
    config = import_config('gs://blub')
    # DONE!

    # write output path to hdfs storage using `output_name` from config
    output_path = os.path.join(
        'hdfs:///', config['script-params']['output_name']['value']
        )

    # copy data (Python code, input VCF, config) to local dataproc instance
    download_data(
        config['script-params']['project-bucket']['value']
    )

    execute_script()
    upload_data(output_path)
