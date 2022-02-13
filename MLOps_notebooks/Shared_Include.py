# Databricks notebook source
import re
import os

current_user_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("user").get()

def get_user_prefix():
  return re.sub(r'[^A-Za-z0-9_]', '_', re.sub(r'^([^@]+)(@.*)?$', r'\1', current_user_name))

current_user_name_prefix = get_user_prefix()

def get_default_path():
  return f'/tmp/{current_user_name_prefix}/ibm-telco-churn'

def get_default_database():
  return f'{current_user_name_prefix}_churn_demo'

spark.sql(f'create database if not exists {get_default_database()}')
spark.sql(f'use {get_default_database()}')

# Set config for database name, file paths, and table names
database_name = get_default_database()

# Paths for various Delta tables
bronze_tbl_path = f'{get_default_path()}/bronze/'
silver_tbl_path = f'{get_default_path()}/silver/'
automl_tbl_path = f'{get_default_path()}/automl-silver/'
telco_preds_path = f'{get_default_path()}/preds/'

bronze_tbl_name = 'bronze_customers'
silver_tbl_name = 'silver_customers'
automl_tbl_name = 'gold_customers'
telco_preds_tbl_name = 'telco_preds'
churn_model_name = f'{current_user_name_prefix}_churn_demo'

print(f'Default database: {get_default_database()}')
print(f'Files are stored in {get_default_path()}')

# COMMAND ----------

import mlflow
from mlflow.utils.rest_utils import http_request
import json

def client():
  return mlflow.tracking.client.MlflowClient()
host_creds = client()._tracking_client.store.get_host_creds()
host = host_creds.host
token = host_creds.token
def mlflow_call_endpoint(endpoint, method, body='{}'):
  if method == 'GET':
      response = http_request(
          host_creds=host_creds, endpoint=f"/api/2.0/mlflow/{endpoint}", method=method, params=json.loads(body))
  else:
      response = http_request(
          host_creds=host_creds, endpoint=f"/api/2.0/mlflow/{endpoint}", method=method, json=json.loads(body))
  return response.json()

# COMMAND ----------

def cleanup_data():
  # Delete the old database and tables if needed
  _ = spark.sql(f'DROP DATABASE IF EXISTS {database_name} CASCADE')

  # Drop any old delta lake files if needed (e.g. re-running this notebook with the same bronze_tbl_path and silver_tbl_path)
  dbutils.fs.rm(bronze_tbl_path, True)
  dbutils.fs.rm(silver_tbl_path, True)
  dbutils.fs.rm(telco_preds_path, True)
