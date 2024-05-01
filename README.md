# Variant Annotation with Hail

**Hail-Annotate** is a Python-based wrapper for Hail which is designed to streamline the annotation of human genetic variants. Users will need to provide an input variant call format (VCF) file, and will receive output annotated with allele frequency information from the [GnomAD database](https://gnomad.broadinstitute.org/).

The following steps are required to launch an annotation task:
1. Ensure you have a local installation of the Hail library.
2. Configure a Google Cloud service account - [setup guide](https://bbowles1.github.io/Hail-Annotate/html/google_setup.html).
3. Edit the config.json to configure your analysis.
4. Upload your VCF to Google cloud.
5. Launch an annotation using:

```
    hailctl dataproc submit gnomad-test /local/path/to/hail_annotation.py \ 
        --config gs://bucket/config.json \ 
        --region <region, ie us-west-1>
```

### Service Account Permissions
This workflow assumes that your service account has `storage.objectAdmin` permission to a bucket used for input and output.

### Full Documentation
Full documentation (including a guide on setting up your Google Cloud analysis) can be found at [https://bbowles1.github.io/Hail-Annotate/index.html](https://bbowles1.github.io/Hail-Annotate/index.html).
