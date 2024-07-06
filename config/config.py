import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.cloud import bigquery

load_dotenv()

environment = os.getenv("ENVIRONMENT")
project_id = os.getenv("PROJECT_ID")
bigquery_dataset = os.getenv("BIGQUERY_DATASET")
service_account_type = os.getenv("SERVICE_ACCOUNT_TYPE")
private_key_id = os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID")
private_key = os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY")
client_email = os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL")
client_id = os.getenv("SERVICE_ACCOUNT_CLIENT_ID")
auth_uri = os.getenv("SERVICE_ACCOUNT_AUTH_URI")
token_uri = os.getenv("SERVICE_ACCOUNT_TOKEN_URI")
auth_provider_x509_cert_url = os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL")
client_x509_cert_url = os.getenv("SERVICE_ACCOUNT_CLIENT_X509_CERT_URL")
user_item_rating_table = os.getenv("USER_ITEM_RATING_TABLE")
model_name_prefix = os.getenv("MODEL_NAME_PREFIX")
table_item_id = os.getenv("TABLE_ITEM_ID")
table_user_id = os.getenv("TABLE_USER_ID")
reservation_id = os.getenv("RESERVATION_ID")
slot_capacity = os.getenv("SLOT_CAPACITY")
storage_bucket_name = os.getenv("STORAGE_BUCKET_NAME")
serving_container_image_uri = os.getenv("SERVING_CONTAINER_IMAGE_URI")
google_project_number = os.getenv("GOOGLE_PROJECT_NUMBER")
google_project_region = os.getenv("GOOGLE_PROJECT_REGION")
ai_platform_api_endpoint = os.getenv("AI_PLATFORM_API_ENDPOINT")
mongodb_uri = os.getenv("MONGODB_URI")
mongodb_database = os.getenv("MONGODB_DATABASE")
mongodb_collection_for_model = os.getenv("MONGODB_COLLECTION_FOR_MODEL")
time_to_run_retrain = os.getenv("TIME_TO_RUN_RETRAIN")
api_secret_key = os.getenv("API_SECRET_KEY")


credentials = service_account.Credentials.from_service_account_info(
    {
        "type": service_account_type,
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": auth_uri,
        "token_uri": token_uri,
        "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
        "client_x509_cert_url": client_x509_cert_url,
    }
)

bq_client = bigquery.Client(credentials=credentials, project=credentials.project_id)
