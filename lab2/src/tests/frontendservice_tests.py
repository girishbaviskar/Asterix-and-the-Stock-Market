import logging
logging.basicConfig(level=logging.ERROR)
import time
import unittest
import os
import shutil
from catalogservice.database import *
import requests
from catalogservice.server import *
from functools import partial
from orderservice.transactionHandler import TransactionHandler
from orderservice.server import *
import threading
from frontend.server import *

start_server_event = threading.Event()


def startCatalogServer(cas_hostname, cas_port, db_path, db_name):
    """
    Starts Catalog service server
    :param cas_hostname:
    :param cas_port:
    :param db_path:
    :param db_name:
    :return:
    """
    db = connectDatabase(db_path=db_path, db_name=db_name)
    CatalogService = partial(CatalogServiceHandler, db)
    catalogServer = ThreadedServer((cas_hostname, cas_port), CatalogService)

    logging.info(f"Catalog Service Server started at http://{cas_hostname}:{cas_port}")

    while not start_server_event.is_set():
        catalogServer.handle_request()
    catalogServer.server_close()
    logging.info(f"Catalog Service Server stopped at http://{cas_hostname}:{cas_port}")
    db.db._file.close()


def startOrderServer(cas_hostname, cas_port, ors_hostname, ors_port, log_path, log_name):
    """
    Starts Order service server
    :param cas_hostname:
    :param cas_port:
    :param ors_hostname:
    :param ors_port:
    :param log_path:
    :param log_name:
    :return:
    """
    transactionHandler = TransactionHandler(log_path=log_path, log_filename=log_name,
                                            catalogServiceHost=cas_hostname,
                                            catalogServicePort=cas_port)
    orderService = partial(OrderServiceHandler, transactionHandler)
    orderServer = ThreadedServer((ors_hostname, ors_port), orderService)

    logging.info(f"Order Service Server started at http://{ors_hostname}:{ors_port}")

    while not start_server_event.is_set():
        orderServer.handle_request()
    orderServer.server_close()
    logging.info(f"Order Service Server stopped at http://{ors_hostname}:{ors_port}")


def startFrontendServer(fes_hostname, fes_port, cas_hostname, cas_port, ors_hostname, ors_port):
    """
    Starts Frontend service server
    :param fes_hostname:
    :param fes_port:
    :param cas_hostname:
    :param cas_port:
    :param ors_hostname:
    :param ors_port:
    :return:
    """
    FrontEndService = partial(FrontEndHandler, cas_hostname, cas_port, ors_hostname,
                              ors_port)
    frontendServer = ThreadedServer((fes_hostname, fes_port), FrontEndService)
    logging.info(f"Frontend Server started at http://{fes_hostname}:{fes_port}")

    while not start_server_event.is_set():
        frontendServer.handle_request()
    frontendServer.server_close()
    logging.info(f"Order Service Server stopped at http://{fes_hostname}:{fes_port}")


class FrontEndTest(unittest.TestCase):
    """
    Defines test cases for the Frontend i.e., full application
    """

    def setUp(self) -> None:
        """
        Setup method for tests
        :return:
        """
        self.cas_hostname = os.getenv("CAS_HOSTNAME", "127.0.0.1")
        self.cas_port = int(os.getenv("CAS_Port", 8083))
        self.ors_hostname = os.getenv("ORS_HOSTNAME", "127.0.0.1")
        self.ors_port = int(os.getenv("CAS_Port", 8085))
        self.fes_hostname = os.getenv("ORS_HOSTNAME", "127.0.0.1")
        self.fes_port = int(os.getenv("CAS_Port", 8089))
        self.db_path = os.getenv("DB_PATH", "./test_db")
        self.db_name = os.getenv("DB_NAME", "test_catalog.db")

        self.log_path = os.getenv("LOG_PATH", "./test_log")
        self.log_name = os.getenv("LOG_NAME", "test_log.log")

        start_server_event.clear()

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        if os.path.exists(os.path.join(self.log_path, self.log_name)):
            shutil.rmtree(self.log_path)

        self.catalogServerProc = threading.Thread(target=startCatalogServer,
                                                  args=(self.cas_hostname, self.cas_port, self.db_path, self.db_name))
        self.catalogServerProc.start()

        self.orderServerProc = threading.Thread(target=startOrderServer, args=(
            self.cas_hostname, self.cas_port, self.ors_hostname, self.ors_port, self.log_path, self.log_name))

        self.orderServerProc.start()

        self.frontendServerProc = threading.Thread(target=startFrontendServer, args=(
            self.fes_hostname, self.fes_port, self.cas_hostname, self.cas_port, self.ors_hostname, self.ors_port))

        self.frontendServerProc.start()

        time.sleep(4)

    def test_lookup(self):
        """
        Tests lookup request
        :return:
        """
        response = requests.get(f"http://{self.fes_hostname}:{self.fes_port}/stocks/BoarCo")
        expected_response = {'data': {'name': 'BoarCo', 'price': 11.54, 'quantity': 100}}

        self.assertEqual(response.json(), expected_response)

    def test_invalidLookup(self):
        """
        Tests an invalid lookup request
        :return:
        """
        response = requests.get(f"http://{self.fes_hostname}:{self.fes_port}/stocks/BoarGo")
        expected_response = {
            "error": {
                "code": 404,
                "message": "stock not found"
            }
        }

        self.assertEqual(response.json(), expected_response)

    def test_order(self):
        """
        Tests a valid order request
        :return:
        """
        order = {
            "name": "GameStart",
            "quantity": 1,
            "type": "sell"
        }
        response = requests.post(f"http://{self.fes_hostname}:{self.fes_port}/orders", json=order)
        expected_response = {
            "data": {
                "transaction_number": 0
            }
        }

        self.assertEqual(response.json(), expected_response)

    def test_invalidOrder(self):
        """
        Tests an invalid order request
        :return:
        """
        order = {
            "name": "GameStart",
            "quantity": 1000,
            "type": "buy"
        }
        response = requests.post(f"http://{self.fes_hostname}:{self.fes_port}/orders", json=order)
        expected_response = {
            "error": {
                "code": 404,
                "message": "transaction unsuccessful"
            }
        }

        self.assertEqual(response.json(), expected_response)

    def test_invalidRequest(self):
        """
        Tests an invalid path for request
        :return:
        """
        response = requests.post(f"http://{self.fes_hostname}:{self.fes_port}/orderP")
        self.assertEqual(response.status_code, 404)
        response = requests.get(f"http://{self.fes_hostname}:{self.fes_port}/stops/BoarCo")
        self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:
        """
        Tear down for tests
        :return:
        """
        start_server_event.set()
        # Dummy request to close the server loop
        requests.get(f"http://{self.fes_hostname}:{self.fes_port}/stocks/BoarCo")
        requests.post(f"http://{self.ors_hostname}:{self.ors_port}/order", json={})

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        if os.path.exists(os.path.join(self.log_path, self.log_name)):
            shutil.rmtree(self.log_path)

        time.sleep(1)


if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)
