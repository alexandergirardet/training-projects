from google.cloud import storage
import os

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.operators.python import BranchPythonOperator


from airflow.models import Variable


BUCKET_NAME = os.environ.get("GCP_GCS_BUCKET")
PROJECT_ID = Variable.get("GCP_PROJECT_ID")

file_url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-01.parquet'
output_url = "/tmp/yellow_tripdata_2022-01.parquet"

def upload_to_gcs(output_url):
    storage_client = storage.Client()

    bucket = storage_client.get_bucket(BUCKET_NAME)

    blob = bucket.blob('raw/data.parquet')

    blob.upload_from_filename(output_url)

    print("Upload to GCS done")

def check_table_exists_in_bq(project_id, dataset_name, table_name):
    # Create a BigQueryHook object
    hook = BigQueryHook(gcp_conn_id='bigquery_connection')

    # Check if the table exists
    if hook.table_exists(project_id, dataset_name, table_name):
        return "no_table"
    else:
        return "create_table"

local_dag = DAG(
    dag_id='web_to_bigquery',
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(0),
        'retries': 1
    }
)

with local_dag:
    extract_data_task = BashOperator(
        task_id='extract_data',
        bash_command=f'curl -o {output_url} {file_url}'
    )

    upload_to_gcs_task = PythonOperator(
        task_id='upload_to_gcs',
        python_callable=upload_to_gcs,
        op_kwargs={'output_url': output_url}
    )

    check_table_exists_in_bq_task = BranchPythonOperator(
        task_id='check_table_exists_in_bq',
        python_callable=check_table_exists_in_bq,
        op_kwargs={
            'project_id': PROJECT_ID,
            'dataset_name': 'training_dataset',
            'table_name': 'yellow_tripdata_2022_01'
        }
    )

    create_table_task = BigQueryCreateEmptyTableOperator(
        gcp_conn_id='bigquery_connection',
        task_id='create_table',
        dataset_id='training_dataset',
        table_id='yellow_tripdata_2022_01'
    )

    upload_to_bq_task = GCSToBigQueryOperator(
        gcp_conn_id='bigquery_connection',
        task_id='upload_to_bq',
        bucket=BUCKET_NAME,
        source_objects=['raw/data.parquet'],
        destination_project_dataset_table='training_dataset.yellow_tripdata_2022_01',
        source_format='PARQUET',
    )

    no_table_task = BashOperator(
        task_id='no_table',
        bash_command='echo "No table"'
    )

    extract_data_task >> upload_to_gcs_task >> check_table_exists_in_bq_task >> [create_table_task, no_table_task] >> upload_to_bq_task
