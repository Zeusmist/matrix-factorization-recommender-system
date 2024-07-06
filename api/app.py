from flask import Flask, request, jsonify
from google_integration.prediction_management import predict_items
from config.config import api_secret_key

app = Flask(__name__)


@app.route("/get_recommendations", methods=["GET"])
def get_recommendations():
    secret_key = request.headers.get("x-api-secret-key")
    if not secret_key or secret_key != api_secret_key:
        return jsonify({"error": "Invalid or missing Secret-Key in headers"}), 401

    userId = request.args.get("userId")
    limit = request.args.get("limit")  # no. of items to return
    skip = request.args.get("skip")  # no. of items to skip

    if not userId:
        return jsonify({"error": "Missing userId parameter"}), 400

    try:
        predicted_itemIds = predict_items({"userId": userId})

        if skip:
            skip = int(skip)
            predicted_itemIds = predicted_itemIds[skip:]

        if limit:
            limit = int(limit)
            predicted_itemIds = predicted_itemIds[:limit]

        return jsonify(predicted_itemIds)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=5000)
