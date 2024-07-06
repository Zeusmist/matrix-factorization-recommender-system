import logging
import threading
import schedule
import asyncio
import time
from data_integration.mongodb_management import save_data_to_file
from data_integration.create_interaction_matrix import create_interaction_matrix
from google_integration.bigquery_table_management import create_table
from google_integration.bigquery_reservation_management import (
    create_reservation,
    create_reservation_assignment,
    delete_reservation,
    delete_assignment,
)
from google_integration.bigquery_model_management import (
    create_model,
    export_model,
    deploy_model,
)
from api.app import app
from config.config import environment, time_to_run_retrain

logging.basicConfig(level=logging.INFO)


def job():
    # Connect MongoDB and save data to file
    asyncio.run(save_data_to_file())

    # Create interaction matrix
    create_interaction_matrix()

    # Create BigQuery table
    create_table()

    # Create BigQuery reservation and assignment
    create_reservation()
    create_reservation_assignment()
    time.sleep(120)

    # Create BigQuery ML model
    create_model()

    # Delete BigQuery reservation and assignment
    delete_assignment()
    delete_reservation()

    # Export and deploy BigQuery ML model
    export_model()
    deploy_model()


def run_scheduler():
    # every day at midnight
    schedule.every().day.at(time_to_run_retrain).do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


def start_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


start_scheduler()


def main():
    if environment == "dev":
        logging.info("Running in development mode")
    elif environment == "prod":
        logging.info("Running in production mode")

    # Start the Flask app
    debug_mode = environment == "dev"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
