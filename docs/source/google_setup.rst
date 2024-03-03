Google Setup
=================

Our goal is to take an input VCF file and annotate it with allele frequency information from the GnomAD database. To do this, we require both a Google Cloud account and a Google Cloud bucket to hold our input files.

Minimizing Google Cloud Costs
-----------------------------

Creating a Google Cloud account will grant you $300 in free credits. My experience annotationg a large VCF file (500k variants) with both genome and exome allele frequency information cost $40 out of these $300 in credits. Your costs may vary depending on the complexity of your pipeline, so carefully monitor your computing costs.

Google will charge you for the following:
A. Transferring data from regions where GnomAD data is hosted to regions where it is not.
B. Storing data in a Google Cloud bucket.
C. Running Google Cloud computational tasks.

Point A can be very expensive if you are not careful. GnomAD uses "requestor pays buckets" which charge you to transfer data from regions where GnomAD is hosted to regions where it is not. GnomAD data is freely available in all US Google Cloud regions. To avoid data transfer costs, you will want to set your region to a US location when initiating a Google Cloud computing task *even if you are not located in the US*. I am using the region `us-west-2` for all examples, although there are many US regions to choose from.

It is harder to minimize our costs for points B and C, but I would generally recommend trying to write efficient code and be wary of storing large files in Google Cloud buckets for extended periods of time. Additionally, when importing GnomAD data, use the GnomAD cloud buckets hosted on Google rather than copying reference data to your own Google Cloud bucket.


Setting Up Your Project
-----------------------------

Creating an account on Google Cloud is straightforward and, importantly, will grant us $300 in free computation credits. Users will need to do the following:

**1. Sign up for Google Cloud.** Users can navigate to the `Google Cloud console <https://console.cloud.google.com/>`_ and sign up for an account using any email address (you do not need a Gmail account to do so).

**3. Install the Google Cloud SDK.** This project will make use of the Google Cloud SDK. While there are some tasks (such as enabling billing or assessing data usage) which are more convenient to do using the Google Cloud console, many of the tasks of uploading data and initiating computing tasks are better done from the command line. You can follow instructions `here to install the Google Cloud SDK on your operating system of choice <https://cloud.google.com/sdk/docs/install>`_.

**4. Create a Google Cloud Project.** Create a new project, which we will use to initiate compute instances and monitor billing. We can use the Google Cloud CLI to do this:
`gcloud projects create example-name-1 --name="GnomAD Project" --labels=type=gnomAD-test``


**2. Enable billing on your Cloud Project.** Within the Cloud console, you can select the "Billing" section (for me, this is hosted on the middle right-side of the console). From there, you can follow `Google's instructions to enable billing for your account. <https://cloud.google.com/billing/docs/how-to/modify-project>`_ Cloud billing will be required to A) launch Google Cloud computation tasks, and B) access GnomAD reference data. 

*Note:* Google does not allow you to set limits on Cloud billing, so I recommend monitoring your usage carefully and testing all code extensively on small test sets. For this project, I opted to test my annotation pipeline by annotating all variants on chromosome 22 with GnomAD allele frequencies, before expanding my analysis to all human chromosomes. For a breakdown of Google Cloud billing costs, please consult this excellent guide from Dan King on how to estimate your cloud billing costs.

**Set a Default Region for your Google Cloud Project.** I have run into the issue where I cannot find a Google Cloud instane unless I specfiy a region to search within. Additionally, at the time of writing users will face significant data transfer costs if they request GnomAD data from somewhere outside of the US. For these reasons, I recommend that you A) set a default, US-based region for your Google Cloud project, and B) specify this region when launching DataProc clusters or other computing tasks. I opted to set my Google Cloud Region as `us-west-1.` I was able to set this as the default for my project using:

.. code-block::bash
    gcloud compute project-info add-metadata \
        --metadata google-compute-default-region=REGION,google-compute-default-zone=ZONE

**5. Create a Google Cloud Bucket.** For this project, we will require a Google Cloud bucket to host our input VCF data, our Python scripts, and our pipeline output. Once you have registered for Google Cloud, you will need to create a new bucket for your project. You can do this from within the Google Cloud console by searching "Cloud Storage" or navigating to `this link <https://console.cloud.google.com/storage/browser?project=sylvan-terra-409723&prefix=&forceOnBucketsSortingFiltering=true>`_. Users can also create a Cloud Bucket from the command line using: `gsutil mb gs://<YOUR_BUCKET_NAME>`.

**6. Tag your Google Cloud Bucket.** Google Cloud Billing will show storage costs, but does not break them down by bucket. Users will need to tag their buckets, and then use these tags to monitor which billing charges correspond to which bucket. Each tag is a `key:value` pair, for example `bucket:gnomad_annotation`. Users can tag their buckets from the command line using: 
`gsutil label ch -l bucket:bucket-tag gs://bucket-path/`.


Enabling a Service Account
--------------------------

We will be using Google's Dataproc computing instances for our annotation pipeline.

Our previous steps created a Google Cloud account with the administrator role. However, Google will not allow you to run Dataproc computing tasks using this administrator role, as this poses a potential security risk to do so. Google instead asks you to use service accounts, which have a narrower set of permissions than the full administrator account, to run computing tasks. If you initiate a Google compute instance without specifying a service account, Google will create a service account automatically and use it to run the Dataproc instance. However, this default account will *not* be able to access our Google Cloud bucket or the input VCF data contained within it.

To solve this issue, we will create a service account and use it to run our computing tasks. The steps are below:

1. Creating a service account. We will use the Google Cloud CLI to make a new service account.

.. code-block:: bash

    gcloud iam service-accounts create test-service-account \
        --description="service account for hail annotation" \
        --display-name="test-service-account"

2. Give your service account the "storage.objectViewer" role to allow it to view Google Cloud buckets within your project.

.. code-block:: bash

    gcloud projects add-iam-policy-binding your-project-name \
        --member="serviceAccount:test-service-account@your-project-name.iam.gserviceaccount.com" \
        --role="roles/storage.objectViewer"

3. Give your service account the "dataproc.worker" role to allow it to initiate Dataproc instances.

.. code-block:: bash

    gcloud projects add-iam-policy-binding your-project-name \
        --member="serviceAccount:test-service-account@your-project-name.iam.gserviceaccount.com" \
        --role="roles/dataproc.worker"

If you need to list your available service accounts, you can use `gcloud auth list` to do so.





OPEN QUESTIONS


Additional Cloud Resources
----------------------------
Dan King, formerly of the Hail Team, has a great `primer for using Hail on Google Cloud <https://github.com/danking/hail-cloud-docs/blob/master/how-to-cloud.md>`_. His example walks you through the basics of initiating a Dataproc instance and launching a simple annotation task.

