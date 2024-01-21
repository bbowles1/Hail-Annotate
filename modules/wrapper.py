#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os

input_vcf = '/tmp/Hail-Annotate/test_files/test.vcf'
output_path = '/tmp/Hail-Annotate/test_files/test_output.tsv'

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

def upload_data(target_for_upload):
    file = os.path.basename(target_for_upload)
    destination_path = os.path.join('gs://hail-annotation-scripts/Hail-Annotate/', file)

    # Run gsutil cp command using subprocess
    subprocess.run(['gsutil', '-m', 'cp', '-r', target_for_upload, destination_path], check=True)
    print(f'File uploaded to {destination_path}')

if __name__ == "__main__":
    download_data()
    execute_script()
    #upload_data(output_path)
