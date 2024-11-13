from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import logging
logging.basicConfig(level=logging.INFO)
import json


class CatalogServiceHandler(BaseHTTPRequestHandler):
    """
    Request handler for Catalog service
    """
    protocol_version = "HTTP/1.1"

    def __init__(self, database, *args):
        """
        Constructor method for CatalogServiceHandler
        :param database:
        :param args:
        """
        self.db = database
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        """
        GET request handler
        :return:
        """
        if self.path.startswith("/lookup/"):
            stockName = self.path.split("/")[-1].strip("/")
            response = self.db.read(stockName)
            if response is None:
                response = {
                    "error": {
                        "code": 404,
                        "message": "stock not found"
                    }
                }
            else:
                response = {"data": {key: response[key] for key in ["name", "price", "quantity"]}}

        else:
            response = {
                "error": {
                    "code": 404,
                    "message": "Invalid request"
                }
            }

        if "error" in response.keys():
            self.send_response(404)
        else:
            self.send_response(200)

        response = json.dumps(response)
        self.send_header("Content-type", "application/json")
        self.send_header("Connection", "Keep-Alive")
        self.send_header("Keep-Alive", "timeout=100, max=300")
        self.send_header("Content-Length", str(len(bytes(response, "utf-8"))))
        self.end_headers()
        self.wfile.write(bytes(response, "utf-8"))

    def do_POST(self):
        """
        POST request handler
        :return:
        """
        content_type = self.headers["Content-Type"]
        content_length = int(self.headers["Content-Length"])

        if self.path == "/update" and content_type == "application/json" and content_length > 0:
            orderString = self.rfile.read(content_length)
            jsonOrder = json.loads(orderString)
            status = self.db.updateStock(jsonOrder["name"], CatalogServiceHandler.updateStockQuantity, jsonOrder)
            response = 200 if status == True else 404
        else:
            response = 404

        self.send_response(response)
        self.send_header("Connection", "Keep-Alive")
        self.send_header("Keep-Alive", "timeout=100, max=300")
        self.send_header("Content-Length", 0)
        self.end_headers()

    @staticmethod
    def updateStockQuantity(value, changeRequest):
        """
        Function to update stock quantity and trading volume
        :param value: current value of stock
        :param changeRequest: modification to make to the value
        :return:
        """
        try:
            value["quantity"] += changeRequest["quantity"]
            value["tradingVolume"] += abs(changeRequest["quantity"])
            status = True
        except:
            status = False
        return value, status


class ThreadedServer(ThreadingMixIn, HTTPServer):
    """
    Threaded server to handle each connection using a different thread
    """
