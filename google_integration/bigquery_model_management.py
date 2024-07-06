import logging
from google.cloud import bigquery
from config.config import *
from google.cloud import aiplatform
from google.api_core.exceptions import AlreadyExists, ResourceExhausted

dataset_path = f"{project_id}.{bigquery_dataset}"
location = "us-central1"


query = f"""
CREATE OR REPLACE MODEL `{dataset_path}.{model_name_prefix}`
OPTIONS(
  model_type='matrix_factorization',
  user_col='{table_user_id}',
  item_col='{table_item_id}',
  rating_col='rating',
  feedback_type='implicit'
) AS
SELECT * FROM `{dataset_path}.{user_item_rating_table}`
"""


def create_model():
    query_job = bq_client.query(query)
    query_job.result()
    logging.info(f"Model '{model_name_prefix}' created.")


def export_model():
    model_id = f"{dataset_path}.{model_name_prefix}"
    export_path = f"gs://{storage_bucket_name}/model_export"

    # Export the model to GCS
    logging.info(f"Exporting model '{model_id}' to '{export_path}'...")
    bq_client.extract_table(
        source=model_id, destination_uris=export_path, source_type="Model"
    ).result()
    logging.info("Model exported to GCS.")

    # Upload the model to Vertex AI model registry
    aiplatform.init(project=project_id, location=location)

    # List all models and find if a model with the same display name already exists
    existing_models = aiplatform.Model.list(
        filter=f'display_name="{model_name_prefix}"'
    )

    if existing_models:
        model_to_delete = existing_models[0]
        logging.info(f"Found existing model with name {model_name_prefix}")

        # Check all endpoints for deployments of this model
        for endpoint in aiplatform.Endpoint.list():
            for deployed_model in endpoint.list_models():
                if deployed_model.model == model_to_delete.resource_name:
                    logging.info(
                        f"Model is deployed to endpoint {endpoint.display_name}. Undeploying model..."
                    )
                    endpoint.undeploy(deployed_model_id=deployed_model.id)

        # Delete the model after undeploying from all endpoints
        logging.info(f"Deleting model: {model_to_delete.display_name}")
        model_to_delete.delete()
        logging.info(f"Deleted model: {model_to_delete.display_name}")

    model = aiplatform.Model.upload(
        display_name=model_name_prefix,
        artifact_uri=export_path,
        serving_container_image_uri=serving_container_image_uri,
    )
    logging.info(f"Model uploaded to AI Platform. {model}")


def evaluate_model():
    model_id = f"{dataset_path}.{model_name_prefix}"
    query = f"""
    SELECT
      *
    FROM
      ML.EVALUATE(MODEL `{model_id}`)
    """

    query_job = bq_client.query(query)
    result = query_job.result()
    for row in result:
        logging.info(row)


def deploy_model():
    try:
        aiplatform.init(project=project_id, location=location)
        endpoint = aiplatform.Endpoint.create(
            display_name=model_name_prefix,
            project=project_id,
            location=location,
            endpoint_id=model_name_prefix.replace("_", "-"),
        )
        logging.info(f"Endpoint created. {endpoint}")
    except AlreadyExists:
        logging.info("Endpoint already exists.")
        endpoint = aiplatform.Endpoint.list(filter=f"display_name={model_name_prefix}")[
            0
        ]
        logging.info(f"Endpoint found. {endpoint}")

    models = aiplatform.Model.list(filter=f"display_name={model_name_prefix}")
    model = models[0].resource_name

    model = aiplatform.Model(model_name=model)
    try:
        deployed_models = endpoint.list_models()
        if deployed_models:
            deployed_endpoint = deployed_models[0]

            if deployed_endpoint.display_name == model_name_prefix:
                # undeploy model
                logging.info("Undeploying model.")
                endpoint.undeploy_all()

        deployed_endpoint = model.deploy(
            endpoint=endpoint,
            traffic_percentage=100,
            machine_type="n2-standard-8",
            deployed_model_display_name=model_name_prefix,
        )
        logging.info(f"Model deployed. {deployed_endpoint}")
    except ResourceExhausted:
        logging.info("Model already deployed.")
        deployed_endpoint = endpoint.list_models()[0]
        logging.info(f"Model found. {deployed_endpoint}")
