Repository structure 

```
|- 00a_lakehouse_etl.py # example of how to ingest data into bronze tables
|- 01_feature_engineering.py # example of how to save features into Feature Store for reuse and lineage tracking
|- 02_automl_baseline.py # training a baseline model with AutoML 
|- 03_webhooks_setup.py  # start here if you already have a model to be productionized
|- 04_from_exp_to_registry.py
|- 05_staging_validation.py. # testing notebook for staging
|- 06_production_validation.py. # testing notebook for production 
|- 07_retrain_churn_automl.py
|- 08_staging_batch_inference.py
Shared_Include.py
```
