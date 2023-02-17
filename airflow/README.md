This project makes use of 3 tools and technologies. Terraform, Airflow, and Docker. The purpose of this project is to create an orchestrated pipeline that will extract data from the web, stage it, process and transform it in a Google Cloud Storage bucket, and then upload it to BigQuery for analysis. Reliability, scalability and maintainability are the primary design concerns when creating data piplines. Using Terraform as our cloud infrastructure as code solution ensures that our cloud configurations can benefit from version control, and [ Insert more information here about terraform ]. Airflow enables us to handle task dependencies in a scalable fashion making use of Dags, an example of it's usefulness in this project is the creation of a BigQuery table prior to loading the data into it. Docker provides us with an isolated environment where we can manage our environment variables such as google cloud credentials, and handles dependencies for airflow as well as provides an internal network for the webserver, postgres database and scheduler to communicate. 

<p align="center">
  <img width="800" height="400" src="https://github.com/alexandergirardet/training-projects/blob/main/airflow/images/airflow_practice_project.drawio.png">
</p>

Docker:

A little bit more information on our Docker configuration. In this project we have two docker related files: Dockerfile and docker-compose.yaml. This project is making use of a technique known as extending docker images. Within a fully fledged production airflow environment we would usually be hosting a reddis broker, and make use of celery to serve several airflow worker nodes that will handle the actual computing needs of our tasks. However due to the small resource requirements of this project, I configured docker to handle it's computing needs in the airflow scheduler. For this reason we needed to provde the airflow scheduler with several libraries that our project makes use of, most notably the google cloud SDK, and the airflow google providers, which gives us access to the GCP airflow operators. The Dockerfile use a pre-configured airflow image as it's base image, and extends it's configurations by installing the libraries within the requirements.txt, and downloads the Google SDK, and extends the path to access the SDK. Within our docker-compose file which handles the serving of the airflow webserver, the scheduler, and the postgres database we use our custom built airflow image with all the dependencies we need. Finally, as shown in the docker-compose.yaml file, we mounted our google credentials file, and created the environment variable GOOGLE_APPLICATION_CREDENTIALS so that our Google cloud storage client can authenticate itself to access our cloud resources. 

Terraform:

Terraform is used in this case to provision our Google cloud bucket, and create a BigQuery dataset. We also made use of the variables.tf file to show the practicality of modularizing our terraform components, and prevent redundancy.

Airflow: 

Within our airflow setup we make use of one dag that contains four tasks in our workflow. The extract_data_task makes use of curl and downloads the dataset to a temporary folder within our scheduler. Once this process is complete, the upload_to_gcs_task, initializes the storage client, and sends the file from the temporary folder to our bucket as specified in our airflow variables. The create_table_task will then create a BigQuery table making use of the BigQueryCreateEmptyTableOperator, and finally upload_to_bq_task uses the GCSToBigQueryOperator to upload the GCS file to BigQuery. It is worth noting that both BigQuery operators required an airflow connection, which is an abstraction of airflow [Look into airflow connections]

In all this project served as a good introduction to the uses and synergies of airflow, terraform and Docker.

TODO:
- Add two dags to check if there is a table already
- Allow it to load more data in 
- Format the code better
