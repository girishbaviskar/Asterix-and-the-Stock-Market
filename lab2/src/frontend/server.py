from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import requests
import logging
logging.basicConfig(level=logging.INFO)
import json

class FrontEndHandler(BaseHTTPRequestHandler):
    """
    Request Handler for FrontEnd service
    """
    protocol_version = "HTTP/1.1"

    def __init__(self, catlogServiceHostname, catlogServicePort, orderServiceHostname, orderServicePort, *args):
        """
        Constructor method for FrontEndServiceHandler
        :param catlogServiceHostname:
        :param catlogServicePort:
        :param orderServiceHostname:
        :param orderServicePort:
        :param args:
        """
        self.catlogServiceHostname = catlogServiceHostname
        self.catlogServicePort = catlogServicePort
        self.orderServiceHostname = orderServiceHostname
        self.orderServicePort = orderServicePort
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        """
        GET request handler
        :return:
        """
        if self.path.startswith("/stocks/"):
            stockName = self.path.split("/")[-1].strip("/")
            requestResponse = requests.get(
                f"http://{self.catlogServiceHostname}:{self.catlogServicePort}/lookup/{stockName}")
            response = requestResponse.json()
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

        if self.path == "/orders" and content_type == "application/json" and content_length > 0:
            orderString = self.rfile.read(content_length)
            jsonOrder = json.loads(orderString)
            requestResponse = requests.post(
                f"http://{self.orderServiceHostname}:{self.orderServicePort}/order", json=jsonOrder)
            response = requestResponse.json()
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

class ThreadedServer(ThreadingMixIn, HTTPServer):
    """
    Threaded server to handle each connection using a different thread
    """
