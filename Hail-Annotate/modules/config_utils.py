#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A set of utilities that read in the Hail annotation config
and perform checks for required fields and their types.
"""

from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden
import json
import re
import os


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
    script_params = ['testing', 'allele-frequency-cutoff', 'project-bucket', 'input_vcf', 'output_name']

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
    config = load_config(gcs_path)

    # check that config fields are expected
    check_fields(config)

    # Check that config types are expected.
    check_config_types(config)

    return config