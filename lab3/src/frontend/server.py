import json
from flask import Flask
from routes import frontend_blueprint
from threading import Lock
from leader_election import perform_election
from cacheout import Cache

def create_frontend():
    """
    Application factory for frontend web application
    :return:
    """
    frontend_config = json.load(open("./config/frontendservice.config"))
    app = Flask(__name__)
    app.config["frontend_config"] = frontend_config
    app.config["cache"] = Cache(maxsize=1000, default=None)
    app.config["leader_addr"] = perform_election(app.config["frontend_config"])
    app.register_blueprint(frontend_blueprint)
    return app