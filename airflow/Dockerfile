FROM apache/airflow:2.5.1-python3.8
RUN pip install joblib==1.1.0
COPY airflow/dags/ /opt/airflow/dags
CMD ["standalone"]
