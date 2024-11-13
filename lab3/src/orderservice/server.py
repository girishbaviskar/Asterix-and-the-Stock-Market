import json
from flask import Flask
from routes import orderservice_blueprint
from threading import Lock
from database import connectDatabase
from utils import find_leader, sync_db_with_leader
from transactionHandler import TransactionHandler


def create_orderservice():
    """
    Application factory for order service web application
    :return:
    """
    orderservice_config = json.load(open("./config/orderservice.config"))
    app = Flask(__name__)
    app.config["orderservice_config"] = orderservice_config
    app.config["replica_id"] = open("./container.name", "r").read().split(".")[0].split("-")[-1]
    db_name = f'replica_{app.config["replica_id"]}.db'
    app.config["db"] = connectDatabase(db_path=orderservice_config["db_path"], db_name=db_name)
    if "leader_addr" not in app.config or app.config["leader_addr"] is None:
        app.config["leader_addr"] = find_leader(orderservice_config)
    app.config["sync_lock"] = Lock()
    app.config["transactionHandler"] = TransactionHandler(orderservice_config, app.config["db"])
    if app.config["leader_addr"] != None:
        sync_db_with_leader(config=orderservice_config, replica_id=app.config["replica_id"],
                            leader_url=app.config["leader_addr"],
                            db=app.config["db"], sync_lock=app.config["sync_lock"],
                            transaction_handler=app.config["transactionHandler"])
    app.register_blueprint(orderservice_blueprint)
    return app
