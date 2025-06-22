# Monitor & Backdoor Cloud Functions

If you have read and write access over a GCP Storage bucket used to store the code of a Cloud Function you can monitor the bucket and submit a backdoored version of the code whenever it gets updated so the new Cloud Function version will execute your code and you will be able to escalate privileges to the Service Account assigned to the Cloud Function.

This script is a probe of concept of the previous attack that will monitor a bucket and submit a zip file with some python code that will print the Access Token from the metadata whenever the code of the function gets updated.

Find more information in https://cloud.hacktricks.xyz/pentesting-cloud/gcp-security/gcp-privilege-escalation/gcp-storage-privesc#cloud-functions

```bash
# Installation
python3 -m pip install -r requirements.txt

# To allow the script to use your gcloud credentials you need to execute first:
gcloud auth application-default login

# Execute the monitoring
python3 backdoor_cf_bucket.py <bucket-name>

#e.g.
python3 backdoor_cf_bucket.py gcf-v2-uploads-30428932595-us-central1
```
