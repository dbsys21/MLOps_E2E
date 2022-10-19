import click
import logging
import time

from databricks_cli.sdk import ApiClient
from databricks_cli.runs.api import RunsApi

@click.command()
@click.option('--notebook-path', required=True)
@click.option('--runtime-version', default="10.3.x-cpu-ml-scala2.12")
@click.option('--node-type', default="Standard_L4s")
@click.option('--num-workers', default="3")
@click.option('--host', required=True)
@click.option('--token', required=True)
def run_notebook(notebook_path, runtime_version, node_type, num_workers, host, token):
    api_client = ApiClient(host=host, token=token)
    runs_api = RunsApi(api_client)
    cluster_conf = {
        'spark_version': runtime_version,
        'node_type_id': node_type,
        'num_workers': num_workers,
        # "autoscale": {
        #     "min_workers": 1,
        #     "max_workers": 6
        # }
        # the aws_attributes are only applicable for databricks on AWS
#         "aws_attributes": {
#         "first_on_demand": 1,
#         "availability": "SPOT_WITH_FALLBACK",
#         "zone_id": "auto",
#         "instance_profile_arn": null,
#         "spot_bid_price_percent": 100,
#         "ebs_volume_type": "GENERAL_PURPOSE_SSD",
#         "ebs_volume_count": 3,
#         "ebs_volume_size": 100
#         },
    }
    run_conf = {
        'new_cluster': cluster_conf,
        'notebook_task': {
            'notebook_path': notebook_path,
        },
    }
    run_id = runs_api.submit_run(json=run_conf)['run_id']
    logging.info(f'Submitted run with ID {run_id}.')

    run_info = runs_api.get_run(run_id)
    run_url = run_info['run_page_url']
    logging.info(f'Run URL: {run_url}')

    run_state = None
    while run_state not in ['TERMINATED', 'SKIPPED', 'INTERNAL_ERROR']:
        logging.info('Waiting for run to finish ...')
        time.sleep(10)
        run_info = runs_api.get_run(run_id)
        run_state = run_info['state']['life_cycle_state']

    
    if run_info['state']['result_state'] == 'SUCCESS':
        logging.info('Run succeeded.')
    else:
        state_message = run_info['state']['state_message']
        raise RuntimeError(f'Run failed: {state_message}. Visit {run_url} to see detailed logs.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s')
    run_notebook()