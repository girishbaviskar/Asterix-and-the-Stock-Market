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

    logging.info(f"Order Service Server started at http://{ors_hostname}:{cas_port}")

    while not start_server_event.is_set():
        orderServer.handle_request()
    orderServer.server_close()
    logging.info(f"Order Service Server stopped at http://{ors_hostname}:{cas_port}")


class OrderServiceTest(unittest.TestCase):
    """
    Defines test cases for the OrderService
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

        time.sleep(4)

    def test_validTransaction(self):
        """
        Tests valid order
        :return:
        """
        order = {
            "name": "GameStart",
            "quantity": 1,
            "type": "sell"
        }
        response = requests.post(f"http://{self.ors_hostname}:{self.ors_port}/order", json=order)
        expected_response = {'data': {'transaction_number': 0}}
        self.assertEqual(response.json(), expected_response)

    def test_invalidTransaction(self):
        """
        Tests invalid order
        :return:
        """
        order = {
            "name": "GameStart",
            "quantity": 1000,
            "type": "buy"
        }
        response = requests.post(f"http://{self.ors_hostname}:{self.ors_port}/order", json=order)
        expected_response = {
            "error": {
                "code": 404,
                "message": "transaction unsuccessful"
            }
        }
        self.assertEqual(response.json(), expected_response)

    def test_invalidStock(self):
        """
        Tests invalid Stock Name
        :return:
        """
        order = {
            "name": "GameStop",
            "quantity": 1000,
            "type": "buy"
        }
        response = requests.post(f"http://{self.ors_hostname}:{self.ors_port}/order", json=order)
        expected_response = {
            "error": {
                "code": 404,
                "message": "transaction unsuccessful"
            }
        }
        self.assertEqual(response.json(), expected_response)

    def tearDown(self) -> None:
        """
        Tear down for tests
        :return:
        """
        start_server_event.set()
        # Dummy request to close the server loop
        requests.get(f"http://{self.cas_hostname}:{self.cas_port}/lookup/BoarCo").json()
        requests.post(f"http://{self.ors_hostname}:{self.ors_port}/order", json={})

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        if os.path.exists(os.path.join(self.log_path, self.log_name)):
            shutil.rmtree(self.log_path)

        time.sleep(1)


if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)
