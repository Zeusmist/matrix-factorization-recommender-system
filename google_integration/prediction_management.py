import logging
from typing import Dict, List, Union
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from config.config import *
from google.protobuf.json_format import MessageToJson
import json


def predict_items(instances: Union[Dict, List[Dict]]):
    """
    `instances` can be either single instance of type dict or a list
    of instances.
    """

    client_options = {"api_endpoint": ai_platform_api_endpoint}

    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    # The format of each instance should conform to the deployed model's prediction input schema.
    instances = instances if isinstance(instances, list) else [instances]
    instances = [
        json_format.ParseDict(instance_dict, Value()) for instance_dict in instances
    ]
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    endpoint = client.endpoint_path(
        project=google_project_number,
        location=google_project_region,
        endpoint=model_name_prefix.replace("_", "-"),
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    logging.info("response")
    logging.info(f" deployed_model_id: {response.deployed_model_id}")

    # The predictions are a google.protobuf.Value representation of the model's predictions.
    predictions = MessageToJson(response._pb)
    predictions = json.loads(predictions)["predictions"]

    return dict(predictions[0])["predicted_itemId"]

    # for prediction in predictions:
    #     logging.info(f" prediction: {dict(prediction)}")
