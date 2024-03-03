#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os

input_vcf = '/tmp/Hail-Annotate/whiffin_simulated_variants_low_likelihood.tsv.gz'
output_path = 'hdfs:///tmp/whiffin_simulated_variants_low_likelihood_annotated.tsv'

def check_output_path(output_path):
    """Check that output path is to HDFS storage.

    :param output_path: Output path on DataProc HDFS storage to use for writing data.
    :type output_path: str

    :raises Exception: Raises Exception of output_path does not contain 'hdfs.'
    """

    if output_path.split('/')[0] != 'hdfs:':
        raise Exception("Output_path must be HDFS!")


# copy everything to local /tmp
def download_data():

    source_bucket = 'gs://hail-annotation-scripts/Hail-Annotate'
    destination_path = '/tmp/'

    # Run gsutil cp command using subprocess
    subprocess.run(['gsutil', '-m', 'cp', '-r', source_bucket, destination_path], check=True)


def execute_script():

    # run main command
    command = [
        'python',
        '/tmp/Hail-Annotate/modules/hail_annotation.py',
        '--input',
        input_vcf,
        '--output',
        output_path,
        '--config',
        '/tmp/Hail-Annotate/config.json'
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


if __name__ == "__main__":
    check_output_path(output_path)
    download_data()
    execute_script()
    upload_data(output_path)
