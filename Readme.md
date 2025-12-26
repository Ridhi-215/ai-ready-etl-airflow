#  AI-Ready ETL Pipeline with Apache Airflow and Google BigQuery

##  Overview

This project implements a **production-style ETL pipeline** using **Apache Airflow**, designed to ingest raw log data from **Google Cloud Storage (GCS)**, perform **AI-ready feature engineering**, and load the transformed data into a **partitioned and clustered Google BigQuery table**.

The pipeline is fully **Dockerized**, monitored through the **Airflow UI**, and includes **failure handling and alerting**, making it suitable for real-world **AI/ML and analytics workflows**.

---

##  Architecture

###  Technologies Used
- Apache Airflow (Docker Compose)
- Google Cloud Storage (Raw data source)
- Python (Data transformation & feature engineering)
- Google BigQuery (Analytics & ML-ready storage)
- SQL (Schema design)
- Docker & Docker Compose

###  High-Level Flow

```text
+---------------------+
|   GCS (Raw Logs)    |
+---------------------+
           |
           v
+---------------------+
|    Airflow DAG      |
+---------------------+
           |
           v
+---------------------+
| Feature Engineering |
|      (Python)       |
+---------------------+
           |
           v
+-------------------------------+
| BigQuery (Partitioned &       |
| Clustered Table)              |
+-------------------------------+
```

---

##  Pipeline Workflow

1. **Extract**
   - Lists raw log files from a GCS bucket using `GCSListObjectsOperator`

2. **Metadata Logging**
   - Logs discovered files using **Airflow XComs** for observability

3. **Transform (AI-Ready Feature Engineering)**
   - Parses TSV log files
   - Cleans and normalizes schema
   - Generates ML-friendly features

4. **Load**
   - Loads transformed data into a **partitioned & clustered BigQuery table**

5. **Monitoring & Alerts**
   - Task retries enabled
   - Email alerts on failure
   - Graph & logs visible in Airflow UI

---

##  AI-Ready Feature Engineering

The pipeline generates the following features suitable for ML tasks such as **anomaly detection**, **classification**, and **time-series analysis**:

| Feature | Description |
|------|------------|
| `event_date` | Date-based partitioning & temporal analysis |
| `hour_of_day` | Captures daily usage patterns |
| `is_error` | Binary failure signal |
| `log_level_encoded` | Numerical encoding for ML models |
| `message_length` | Text-based feature for log intelligence |
| `service_error_rate` | Statistical feature per service |

---

##  BigQuery Table Design

###  Table Name
log_analytics
ai_log_features


###  Schema Highlights
- **Partitioned by:** `event_date`
- **Clustered by:** `service`, `log_level`

###  Benefits
- Fast time-based queries
- Efficient ML feature retrieval
- Scalable analytics and cost optimization

---

##  Monitoring & Failure Handling

- DAG retries configured
- Email alerts enabled on task failure
- Airflow UI used for:
  - DAG status monitoring
  - Task-level logs
  - Debugging & recovery

> Intentional failure testing was performed to validate alerting and monitoring behavior.

---

##  How to Run the Project

### 1️.Start Airflow
```bash
docker compose up airflow-init
docker compose up -d
```

### 2️.Access Airflow UI
```bash
http://127.0.0.1:8080
```

Credentials
```bash
Username: airflow

Password: airflow
```
---

## Project Structure

```text
ai-ready-etl-airflow/
│
├── dags/
│   └── gcs_log_extract_dag.py
├── gcp/
│   └── airflow-etl-sa.json   # (ignored in GitHub)
├── logs/
├── plugins/
├── docker-compose.yaml
├── requirements.txt
├── .env
└── README.md
```

---
## 📸 Screenshots & Execution Evidence

### 1. GCS bucket with raw log file
![GCS bucket with sample_logs.csv](screenshots/GCS_bucket_with_sample_logs.csv.png)

---

### 2. BigQuery dataset created (`log_analytics`)
![BigQuery dataset log_analytics](screenshots/BigQuery_dataset_log_analytics.png)

---

### 3. GCP project dashboard
![GCP project dashboard](screenshots/GCP_project_dashboard.png)

---

### 4. Airflow UI home page (DAGs view)
![Airflow UI home (DAGs page)](screenshots/Airflow_UI_home_DAGs_page.png)

---

### 5. Docker Desktop showing running containers
![Docker Desktop showing running containers](screenshots/Docker_Desktop_showing_running_containers.png)

---

### 6. Terminal output showing `docker compose up -d`
![Terminal showing docker compose up -d](screenshots/Terminal_showing_docker_compse_up_-d.png)

---

### 7. GCP service account created for Airflow
![Service account created](screenshots/Service_account_created.png)

---

### 8. Assigned IAM roles (BigQuery & Storage)
![Assigned roles (BigQuery + Storage)](screenshots/Assigned_roles_BigQuery_Storage.png)

---

### 9. Airflow Connections page (`google_cloud_default`)
![Airflow Connections page showing google_cloud_default](screenshots/Airflow_Connections_page_showing_google_cloud_default.png)

---

### 10. Airflow DAGs page showing `gcs_log_extract_dag`
![Airflow DAGs page showing gcs_log_extract_dag](screenshots/Airflow_DAGs_page_showin_gcs_log_extract_dag.png)

---

### 11. Graph view with extraction task succeeded
![Graph view with task succeeded (green)](screenshots/Graph_view_with_task_succeeded.png)

---

### 12. Task logs showing GCS file name
![Task logs showing the GCS file name](screenshots/Task_logs_showing_the_GCS_file_name.png)

---

### 13. Graph view showing extraction and transformation tasks successful
![Graph view showing all 3 tasks successful](screenshots/Graph_view_showing_all_3_tasks_successful.png)

---

### 14. BigQuery table schema with partitioning
![BigQuery table schema + partitioning info](screenshots/BigQuery_table_schema_partitioning_info.png)

---

### 15. Airflow Graph view with full pipeline successful
![Airflow Graph View with all tasks green](screenshots/Airflow_Graph_View_with_all_tasks_green.png)

---

### 16. BigQuery query result with loaded data
![BigQuery query result with data](screenshots/BigQuery_query_result_with_data.png)

---

### 17. Airflow logs confirming rows loaded into BigQuery
![Logs of load_to_bigquery showing rows loaded](screenshots/Logs_of_load_to_bigquery_showing_rows_loaded.png)

---

### 18. DAG code showing email alert configuration
![DAG code showing email_on_failure true](screenshots/DAG_code_showing-email_on_failure-true.png)

---

### 19. DAG run marked as Failed (intentional test)
![DAG run marked Failed](screenshots/DAG _run_marked_Failed.png)

---

### 20. Task logs showing intentional failure
![Task logs showing intentional failure](screenshots/Task_logs_showing_intentional_failure.png)

---

### 21. Final successful DAG run after recovery
![Final screenshot with all tasks green](screenshots/final_screenshot_with_all_tasks_green.png)



## Example BigQuery Validation Query
```text
SELECT
  event_date,
  service,
  log_level,
  is_error,
  message_length
FROM `ai-ready-etl-pipeline.log_analytics.ai_log_features`
LIMIT 10;
```

## Key Takeaways

End-to-end ETL orchestration using Apache Airflow

AI-focused feature engineering within the pipeline

Production-grade BigQuery partitioning & clustering

Robust handling of real-world data issues

Monitoring, retries, and alerting included

## Author

Ridhi

AI Engineer Candidate

