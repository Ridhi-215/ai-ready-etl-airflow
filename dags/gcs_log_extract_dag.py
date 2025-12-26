from airflow import DAG
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.utils.dates import days_ago
from datetime import timedelta

import pandas as pd
from io import StringIO


# -------------------- DEFAULT ARGS --------------------
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["gunturridhi@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# -------------------- TASK FUNCTIONS --------------------
def log_gcs_files(ti):
    files = ti.xcom_pull(task_ids="list_log_files_in_gcs")
    print("Files found in GCS bucket:")
    if files:
        for f in files:
            print(f)
    else:
        print("No files found.")


def transform_logs():
    # TEMPORARY: Intentional failure to test alerting and monitoring
    # raise ValueError("Intentional failure to test alerting and monitoring")

    bucket_name = "ai-log-raw-data-215"
    object_name = "sample_logs.csv"

    gcs_hook = GCSHook(gcp_conn_id="google_cloud_default")

    file_content = gcs_hook.download(
        bucket_name=bucket_name,
        object_name=object_name
    ).decode("utf-8")

    # TSV (tab-separated) logs
    df = pd.read_csv(StringIO(file_content), sep="\t")

    # -------- NORMALIZE SCHEMA --------
    print("Original columns:", df.columns.tolist())
    df.columns = df.columns.str.strip().str.lower()
    print("Normalized columns:", df.columns.tolist())

    required_columns = {"timestamp", "log_level", "service", "message", "user_id"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Missing required columns. Found: {df.columns.tolist()}")

    # -------- FEATURE ENGINEERING --------
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["event_date"] = df["timestamp"].dt.date
    df["hour_of_day"] = df["timestamp"].dt.hour

    df["is_error"] = (df["log_level"] == "ERROR").astype(int)

    log_level_map = {"INFO": 0, "WARN": 1, "ERROR": 2}
    df["log_level_encoded"] = df["log_level"].map(log_level_map)

    df["message_length"] = df["message"].astype(str).apply(len)

    service_error_rate = df.groupby("service")["is_error"].mean()
    df["service_error_rate"] = df["service"].map(service_error_rate)

    print("Transformed Data Sample:")
    print(df.head())

    return df.to_csv(index=False)


def load_to_bigquery(ti):
    csv_data = ti.xcom_pull(task_ids="transform_logs_feature_engineering")

    if not csv_data:
        raise ValueError("No transformed data received from XCom")

    df = pd.read_csv(StringIO(csv_data))

    # -------- FIX DATA TYPES --------
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["event_date"] = pd.to_datetime(df["event_date"]).dt.date

    df["hour_of_day"] = df["hour_of_day"].astype("int64")
    df["log_level_encoded"] = df["log_level_encoded"].astype("int64")
    df["message_length"] = df["message_length"].astype("int64")
    df["is_error"] = df["is_error"].astype("int64")
    df["service_error_rate"] = df["service_error_rate"].astype("float64")
    df["user_id"] = df["user_id"].astype("int64")

    project_id = "ai-ready-etl-pipeline"
    dataset_id = "log_analytics"
    table_id = "ai_log_features"
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    bq_hook = BigQueryHook(
        gcp_conn_id="google_cloud_default",
        use_legacy_sql=False
    )

    client = bq_hook.get_client()
    job = client.load_table_from_dataframe(df, table_ref)
    job.result()

    print(f"Loaded {job.output_rows} rows into {table_ref}")


# -------------------- DAG DEFINITION --------------------
with DAG(
    dag_id="gcs_log_extract_dag",
    default_args=default_args,
    description="End-to-end AI-ready ETL pipeline: GCS → Feature Engineering → BigQuery",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["etl", "gcs", "bigquery", "ai"],
) as dag:

    list_gcs_logs = GCSListObjectsOperator(
        task_id="list_log_files_in_gcs",
        bucket="ai-log-raw-data-215",
        gcp_conn_id="google_cloud_default",
    )

    log_files = PythonOperator(
        task_id="log_gcs_files",
        python_callable=log_gcs_files,
    )

    transform_task = PythonOperator(
        task_id="transform_logs_feature_engineering",
        python_callable=transform_logs,
    )

    load_bq_task = PythonOperator(
        task_id="load_to_bigquery",
        python_callable=load_to_bigquery,
    )

    list_gcs_logs >> log_files >> transform_task >> load_bq_task
