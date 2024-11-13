from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import logging
logging.basicConfig(level=logging.INFO)
import json


class OrderServiceHandler(BaseHTTPRequestHandler):
    """
    Request Handler for Order Service
    """
    protocol_version = "HTTP/1.1"

    def __init__(self, transactionHandler, *args):
        """
        Constructor method for OrderServiceHandler
        :param transactionHandler:
        :param args:
        """
        self.transactionHandler = transactionHandler
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        """
        POST Request Handler
        :return:
        """
        content_type = self.headers["Content-Type"]
        content_length = int(self.headers["Content-Length"])

        if self.path == "/order" and content_type == "application/json" and content_length > 0:
            orderString = self.rfile.read(content_length)
            jsonOrder = json.loads(orderString)

            transactionID = None
            if (all(key in jsonOrder.keys() for key in ("name", "quantity", "type"))):
                transactionID = self.transactionHandler.performTransaction(jsonOrder)

            if transactionID != None:
                response = {"data":{"transaction_number": transactionID}}
            else:
                response = {
                    "error": {
                        "code": 404,
                        "message": "transaction unsuccessful"
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

class ThreadedServer(ThreadingMixIn, HTTPServer):
    """
    Threaded server to handle each connection using a different thread
    """
