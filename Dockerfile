FROM apache/airflow:3.3.1

# dbt lives in its own virtualenv so its dependencies never clash with Airflow's pinned ones.
# Airflow tasks will call /opt/airflow/dbt_venv/bin/dbt.
RUN python -m venv /opt/airflow/dbt_venv \
 && /opt/airflow/dbt_venv/bin/pip install --no-cache-dir dbt-duckdb

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
