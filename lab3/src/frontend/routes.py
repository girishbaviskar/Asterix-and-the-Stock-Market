from flask import current_app, Blueprint, request, jsonify
import requests
import json
from leader_election import perform_election

frontend_blueprint = Blueprint("frontend_bp", __name__)


@frontend_blueprint.route('/stocks/<stock_name>', methods=['GET'])
def lookup(stock_name):
    """
    Lookup request route
    :param stock_name:
    :return:
    """
    response = None
    try:
        if current_app.config["frontend_config"]["cache"]:
            response = current_app.config["cache"].get(stock_name)
        if response is None:
            catalog_url = f"{current_app.config['frontend_config']['catalogservice_url']}/lookup/{stock_name}"
            response = requests.get(catalog_url).json()
            current_app.config["cache"].set(stock_name, response)
    except:
        response = {
            "error": {
                "code": 500,
                "message": "Server did not respond"
            }
        }

    status_code = 200
    if "error" in response:
        status_code = response["error"]["code"]

    return jsonify(response), status_code


@frontend_blueprint.route('/orders/<order_id>', methods=['GET'])
@frontend_blueprint.route('/orders', methods=['POST'])
def order(order_id=None):
    """
    Order request routes
    :param order_id:
    :return:
    """
    retries = 0
    response = None
    if request.method == "POST":
        while response is None and retries < current_app.config["frontend_config"]["max_retries"]:

            try:
                requested_order = request.get_json()
                order_url = f"{current_app.config['leader_addr']}/orders"
                response = requests.post(order_url, json=requested_order).json()
            except:
                current_app.config["leader_addr"] = perform_election(current_app.config["frontend_config"])
                response = None
                retries += 1

    elif request.method == "GET":
        while response is None and retries < current_app.config["frontend_config"]["max_retries"]:
            try:
                order_url = f"{current_app.config['leader_addr']}/orders/{order_id}"
                response = requests.get(order_url).json()
            except:
                current_app.config["leader_addr"] = perform_election(current_app.config["frontend_config"])
                response = None
                retries += 1

    if response is None:
        response = {
            "error": {
                "code": 500,
                "message": "Server did not respond"
            }
        }

    status_code = 200
    if "error" in response:
        status_code = response["error"]["code"]

    return jsonify(response), status_code


@frontend_blueprint.route('/invalidate/<secret_key>/<stock_name>', methods=['GET'])
def invalidateCache(secret_key=None, stock_name=None):
    """
    Cache invalidation route
    :param secret_key:
    :param stock_name:
    :return:
    """
    if secret_key == current_app.config["frontend_config"]["secret_key"]:
        if current_app.config["cache"].get(stock_name):
            current_app.config["cache"].delete(stock_name)
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "fail"}), 511


@frontend_blueprint.route('/<secret_key>/whoisleader', methods=['GET'])
def whoisleader(secret_key=None):
    """
    Returns the order service leader address
    :param secret_key:
    :return:
    """
    if secret_key == current_app.config["frontend_config"]["secret_key"]:
        if "leader_addr" in current_app.config:
            return current_app.config["leader_addr"], 200
        else:
            return "None", 200
    else:
        return "Incorrect secret key", 511
