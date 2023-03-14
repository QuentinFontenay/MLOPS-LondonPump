FROM apache/airflow:2.5.1-python3.8
RUN pip install joblib==1.1.0
COPY airflow/dags/ /opt/airflow/dags
ENV _AIRFLOW_DB_UPGRADE=true
ENV _AIRFLOW_WWW_USER_CREATE=true
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false
ENV AIRFLOW__CORE__dags_folder=/opt/airflow/dags
ENV AIRFLOW__WEBSERVER__BASE_URL=http://airflowlondonfire.azurewebsites.net:8080
EXPOSE 8080
CMD ["standalone"]
