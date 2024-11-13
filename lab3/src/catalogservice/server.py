import json
from database import connectDatabase
from flask import Flask
from routes import catalogservice_blueprint

def create_catalogservice():
    """
    Application factory for catalog service web application
    :return:
    """
    config = json.load(open("./config/catalogservice.config"))
    database = connectDatabase(db_path=config["DB_PATH"], db_name=config["DB_NAME"])
    app = Flask(__name__)
    app.config["catalog_database"] = database
    app.config["catalogservice_config"] = config
    app.register_blueprint(catalogservice_blueprint)
    return app
