from flask import current_app, Blueprint, request
import json
from utils import updateStockQuantity, invalidateFrontendCache
from database import populateDatabase

catalogservice_blueprint = Blueprint("catalogservice_bp", __name__)


@catalogservice_blueprint.route('/lookup/<stock_name>', methods=['GET'])
def lookup(stock_name):
    """
    Lookup request
    :param stock_name:
    :return:
    """
    response = current_app.config["catalog_database"].read(stock_name)
    if response is None:
        response = {
            "error": {
                "code": 404,
                "message": "stock not found"
            }
        }
    else:
        response = {"data": {key: response[key] for key in ["name", "price", "quantity"]}}

    status_code = 404 if "error" in response.keys() else 200
    response = json.dumps(response)
    return response, status_code


@catalogservice_blueprint.route('/update', methods=['POST'])
def order():
    """
    Performs order update
    :return:
    """
    order_content = request.get_json()
    if order_content is None:
        return 404
    else:
        # The updateStock method is thread-safe
        status = current_app.config["catalog_database"].updateStock(order_content["name"], updateStockQuantity,
                                                                    order_content)

        if current_app.config["catalogservice_config"]["cache"]:
            invalidateFrontendCache(current_app.config["catalogservice_config"], order_content["name"])

    return json.dumps({"status": status}), 200 if status else 404

@catalogservice_blueprint.route('/clearDB/<secret_key>', methods=['GET'])
def clearDB(secret_key=None):
    """
    Resets DB
    :param secret_key:
    :return:
    """
    if secret_key == current_app.config["catalogservice_config"]["secret_key"]:
        current_app.config["catalog_database"].clear()
        populateDatabase(current_app.config["catalog_database"])
        return json.dumps({"status": "cleared"}), 200
    else:
        return json.dumps({"status": "not authenticated"}), 511
