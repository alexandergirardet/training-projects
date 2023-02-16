Okay I am giving myself this challenge.

I will use terraform to deploy the tools necessary in this project, which is a BigQuery dataset, and a Cloud bucket. From there I will create a dag that extracts data from the web, loads it locally. The next dag will take that data, split it up into 5 files, and load them into cloud storage. From there I will have another dag that loads the data into BigQuery. I would like to also make it in a way so that I can add more data to the dataset. 

1) Terraform. This is done
2) Extract data
3) Partition and load to GCS
4) Load from GCS to BigQuery

This will all be run on Docker.