import logging
from google.cloud import bigquery
from config.config import *
from google.api_core.exceptions import NotFound


dataset_id = bigquery_dataset
table_id = user_item_rating_table

schema = [
    bigquery.SchemaField("userId", "STRING"),
    bigquery.SchemaField("itemId", "STRING"),
    bigquery.SchemaField("rating", "INTEGER"),
]

fully_qualified_table_id = f"{project_id}.{dataset_id}.{table_id}"


def create_table():
    try:
        bq_client.get_table(fully_qualified_table_id)
        logging.info(f"Table '{fully_qualified_table_id}' found, deleting it.")
        bq_client.delete_table(fully_qualified_table_id)
        logging.info(f"Table '{fully_qualified_table_id}' successfully deleted.")
    except NotFound:
        logging.info(
            f"Table '{fully_qualified_table_id}' does not exist, creating a new one."
        )

    # Create a table
    table = bigquery.Table(f"{project_id}.{dataset_id}.{table_id}", schema=schema)
    table = bq_client.create_table(table)

    logging.info(
        f"Created table '{fully_qualified_table_id}' in dataset '{dataset_id}' with schema:"
    )

    # Load data into the table
    filename = "data_files/user_item_rating.csv"
    with open(filename, "rb") as source_file:
        job = bq_client.load_table_from_file(
            source_file,
            fully_qualified_table_id,
            job_config=bigquery.LoadJobConfig(
                skip_leading_rows=1,
                autodetect=True,
                source_format=bigquery.SourceFormat.CSV,
            ),
        )

    # Waits for the job to complete
    logging.info(f"result {job.result()}")
