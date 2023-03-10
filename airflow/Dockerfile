FROM puckel/docker-airflow
RUN pip install joblib==1.1.0
COPY airflow/dags/ /opt/airflow/dags
CMD ["standalone"]
