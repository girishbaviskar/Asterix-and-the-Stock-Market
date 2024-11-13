import logging

from flask import current_app, Blueprint, request, jsonify, after_this_request
from utils import *

orderservice_blueprint = Blueprint("orderservice_bp", __name__)


@orderservice_blueprint.route("/ping", methods=["GET"])
def ping():
    """
    Health ping request route
    :return:
    """
    return current_app.config["replica_id"], 200


@orderservice_blueprint.route("/orders/<order_id>", methods=["GET"])
@orderservice_blueprint.route("/orders", methods=["POST"])
def order(order_id=None):
    """
    Routes for order and order lookup requests
    :param order_id:
    :return:
    """
    if request.method == "GET":

        order_data = current_app.config["db"].read(int(order_id))

        if order_data:
            return jsonify({'data': order_data}), 200
        else:
            error_response = {
                "error": {
                    "code": 404,
                    "message": "order not found"
                }
            }

            return jsonify(error_response), 404

    if request.method == "POST":

        with current_app.config["sync_lock"]:
            order_json = request.get_json()
            transaction_log = None
            if (all(key in order_json.keys() for key in ("name", "quantity", "type"))):
                transaction_log = current_app.config["transactionHandler"].performTransaction(order_json,
                                                                                              current_app.config["db"],
                                                                                              current_app.config)
            if transaction_log != None:
                response = {"data": {"transaction_number": transaction_log["transactionID"]}}

            else:
                response = {
                    "error": {
                        "code": 404,
                        "message": "transaction unsuccessful"
                    }
                }

        if "error" in response.keys():
            return jsonify(response), 404
        else:
            return jsonify(response), 200


@orderservice_blueprint.route("/syncSendMulti/<current_id>", methods=["GET"])
def sync_send_multi(current_id=0):
    """
    Route for replicas to request leader for synchronization. The leader sends all data starting
    given id
    :param current_id: transaction_id from which the logs are requested
    :return:
    """
    with current_app.config["sync_lock"]:
        data = current_app.config["db"].get_data_from(current_id=int(current_id))
        return jsonify(data), 200


@orderservice_blueprint.route("/syncReceive", methods=["POST"])
def sync_receive():
    """
    Route for leader to send new order log to the replicas for synchronization
    :return:
    """
    data = request.get_json()
    current_app.config["db"].write(data["transactionID"], data)
    current_app.config["transactionHandler"].updateLastTransactionState(current_app.config["db"])

    return jsonify({"status": True}), 200


@orderservice_blueprint.route("/announceLeader/<leader_id>", methods=["GET"])
def announceLeader(leader_id=None):
    """
    To announce the current leader to all replicas. Used by frontend after leader election.
    :param leader_id:
    :return:
    """
    current_app.config["leader_addr"] = current_app.config["orderservice_config"]["replica_addr"].format(leader_id)
    if current_app.config["leader_addr"] is not None:
        sync_db_with_leader(config=current_app.config["orderservice_config"],
                            replica_id=current_app.config["replica_id"],
                            leader_url=current_app.config["leader_addr"],
                            db=current_app.config["db"], sync_lock=current_app.config["sync_lock"],
                            transaction_handler=current_app.config["transactionHandler"])
        return "success", 200
    else:
        return "fail", 500


@orderservice_blueprint.route("/getLeader", methods=["GET"])
def getLeader():
    """
    Returns the current leader
    :return:
    """
    return current_app.config["leader_addr"], 200

@orderservice_blueprint.route('/clearDB/<secret_key>', methods=['GET'])
def clearDB(secret_key=None):
    """
    Clears the DB for leader and all the replicas
    :param secret_key:
    :return:
    """
    if secret_key == current_app.config["orderservice_config"]["secret_key"]:
        my_url = current_app.config["orderservice_config"]["replica_addr"].format(current_app.config["replica_id"])
        current_app.config["db"].clear()
        current_app.config["transactionHandler"].updateLastTransactionState(current_app.config["db"])
        if my_url == current_app.config["leader_addr"]:
            send_clear(config=current_app.config["orderservice_config"], leader_url=current_app.config["leader_addr"])
        return jsonify({"status": "cleared"}), 200
    else:
        return jsonify({"status": "not authenticated"}), 511
