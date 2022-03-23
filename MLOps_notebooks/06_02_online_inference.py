# Databricks notebook source
# MAGIC %md
# MAGIC ## Churn Prediction Batch Inference
# MAGIC 
# MAGIC <img src="https://github.com/RafiKurlansik/laughing-garbanzo/blob/main/step6.png?raw=true">

# COMMAND ----------

# MAGIC %md
# MAGIC #### Load Model
# MAGIC 
# MAGIC Loading as a Spark UDF to set us up for future scale.

# COMMAND ----------

# MAGIC %run ./Shared_Include

# COMMAND ----------

# import mlflow
# model = mlflow.pyfunc.spark_udf(spark, model_uri=f"models:/{churn_model_name}/staging") # may need to replace with your own model name

# COMMAND ----------

# MAGIC %md
# MAGIC #### Load Features

# COMMAND ----------

from databricks.feature_store import FeatureStoreClient

fs = FeatureStoreClient()
features = fs.read_table(f'{database_name}.churn_features')

# COMMAND ----------

sample = features.toPandas()
# spark_df = createDataFrame(pandas_df)

# COMMAND ----------

type(sample.iloc[[0]])

# COMMAND ----------

# MAGIC %md
# MAGIC #### Online Inference

# COMMAND ----------

scoring_uri = 'https://adb-984752964297111.11.azuredatabricks.net/model/leo_mao_churn_demo/1/invocations'

# COMMAND ----------

import os
import json
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
# prediction = query_endpoint_example(scoring_uri=scoring_uri, inputs=json.loads(sample_json), service_key=token)

# COMMAND ----------

import os
import requests
import numpy as np
import pandas as pd

def create_tf_serving_json(data):
  return {'inputs': {name: data[name].tolist() for name in data.keys()} if isinstance(data, dict) else data.tolist()}

def score_model(dataset):
  headers = {'Authorization': f'Bearer {token}'}
  data_json = dataset.to_dict(orient='split') if isinstance(dataset, pd.DataFrame) else create_tf_serving_json(dataset)
  response = requests.request(method='POST', headers=headers, url=scoring_uri, json=data_json)
  if response.status_code != 200:
    raise Exception(f'Request failed with status {response.status_code}, {response.text}')
  return response.json()

# COMMAND ----------

# MAGIC %sh
# MAGIC 
# MAGIC ls /Files

# COMMAND ----------

# MAGIC %sh 
# MAGIC 
# MAGIC curl \
# MAGIC   -u token:$DATABRICKS_TOKEN \
# MAGIC   -X POST \
# MAGIC   -H "Content-Type: application/json; format=pandas-records" \
# MAGIC   -d@data.json \
# MAGIC   https://adb-984752964297111.11.azuredatabricks.net/model/leo_mao_churn_demo/1/invocations

# COMMAND ----------

result1 = score_model(sample.iloc[[0]])
print(f"prediction={result1}")

# COMMAND ----------

data = pd.DataFrame([
  {
    "customerID": "6849-OYAMU",
    "seniorCitizen": 0,
    "tenure": 19,
    "monthlyCharges": 100,
    "totalCharges": 1888.65,
    "gender_Female": 0,
    "gender_Male": 1,
    "partner_No": 0,
    "partner_Yes": 1,
    "dependents_No": 0,
    "dependents_Yes": 1,
    "phoneService_No": 0,
    "phoneService_Yes": 1,
    "multipleLines_No": 1,
    "multipleLines_Nophoneservice": 0,
    "multipleLines_Yes": 0,
    "internetService_DSL": 0,
    "internetService_Fiberoptic": 1,
    "internetService_No": 0,
    "onlineSecurity_No": 1,
    "onlineSecurity_Nointernetservice": 0,
    "onlineSecurity_Yes": 0,
    "onlineBackup_No": 0,
    "onlineBackup_Nointernetservice": 0,
    "onlineBackup_Yes": 1,
    "deviceProtection_No": 1,
    "deviceProtection_Nointernetservice": 0,
    "deviceProtection_Yes": 0,
    "techSupport_No": 0,
    "techSupport_Nointernetservice": 0,
    "techSupport_Yes": 1,
    "streamingTV_No": 0,
    "streamingTV_Nointernetservice": 0,
    "streamingTV_Yes": 1,
    "streamingMovies_No": 0,
    "streamingMovies_Nointernetservice": 0,
    "streamingMovies_Yes": 1,
    "contract_Month-to-month": 0,
    "contract_Oneyear": 1,
    "contract_Twoyear": 0,
    "paperlessBilling_No": 1,
    "paperlessBilling_Yes": 0,
    "paymentMethod_Banktransfer-automatic": 1,
    "paymentMethod_Creditcard-automatic": 0,
    "paymentMethod_Electroniccheck": 0,
    "paymentMethod_Mailedcheck": 0
  }
])

# COMMAND ----------

{
  "customerID": "6849-OYAMU",
  "seniorCitizen": 0,
  "tenure": 19,
  "monthlyCharges": 100,
  "totalCharges": 1888.65,
  "gender_Female": 0,
  "gender_Male": 1,
  "partner_No": 0,
  "partner_Yes": 1,
  "dependents_No": 0,
  "dependents_Yes": 1,
  "phoneService_No": 0,
  "phoneService_Yes": 1,
  "multipleLines_No": 1,
  "multipleLines_Nophoneservice": 0,
  "multipleLines_Yes": 0,
  "internetService_DSL": 0,
  "internetService_Fiberoptic": 1,
  "internetService_No": 0,
  "onlineSecurity_No": 1,
  "onlineSecurity_Nointernetservice": 0,
  "onlineSecurity_Yes": 0,
  "onlineBackup_No": 0,
  "onlineBackup_Nointernetservice": 0,
  "onlineBackup_Yes": 1,
  "deviceProtection_No": 1,
  "deviceProtection_Nointernetservice": 0,
  "deviceProtection_Yes": 0,
  "techSupport_No": 0,
  "techSupport_Nointernetservice": 0,
  "techSupport_Yes": 1,
  "streamingTV_No": 0,
  "streamingTV_Nointernetservice": 0,
  "streamingTV_Yes": 1,
  "streamingMovies_No": 0,
  "streamingMovies_Nointernetservice": 0,
  "streamingMovies_Yes": 1,
  "contract_Month-to-month": 0,
  "contract_Oneyear": 1,
  "contract_Twoyear": 0,
  "paperlessBilling_No": 1,
  "paperlessBilling_Yes": 0,
  "paymentMethod_Banktransfer-automatic": 1,
  "paymentMethod_Creditcard-automatic": 0,
  "paymentMethod_Electroniccheck": 0,
  "paymentMethod_Mailedcheck": 0
}

# COMMAND ----------

result2 = score_model(data)
print(f"prediction={result2}")
