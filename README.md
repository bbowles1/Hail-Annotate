# Hail-Annotate

**Hail-Annotate** is a Python library that annotates variant call format (VCF) files with GnomAD allele frequency information.
This repo assumes the user is familiar with the variant call format (link) and the GnomAD Project (link).

Configure the config.json and launch an annotation task using:
```
    hailctl dataproc submit gnomad-test /local/path/to/hail_annotation.py \ 
        --config gs://hail-annotation-scripts/test_config.json \ 
        --region us-west1
```

### Service Account Permissions
This workflow assumes that your service account has "storage.objectAdmin" permission to a bucket used for input and output.