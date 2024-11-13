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


class TransactionHandlerTest(unittest.TestCase):
    """
    Defines test cases for the Transaction Handler
    """

    def setUp(self) -> None:
        """
        Setup method for tests
        :return:
        """
        self.cas_hostname = os.getenv("CAS_HOSTNAME", "127.0.0.1")
        self.cas_port = int(os.getenv("CAS_Port", 8083))
        self.db_path = os.getenv("DB_PATH", "./test_db")
        self.db_name = os.getenv("DB_NAME", "test_catalog.db")

        self.log_path = os.getenv("DB_PATH", "./test_log")
        self.log_name = os.getenv("DB_NAME", "test_log.log")

        start_server_event.clear()

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        if os.path.exists(os.path.join(self.log_path, self.log_name)):
            shutil.rmtree(self.log_path)

        self.serverProc = threading.Thread(target=startCatalogServer,
                                           args=(self.cas_hostname, self.cas_port, self.db_path, self.db_name))
        self.serverProc.start()
        time.sleep(2)

        self.transactioner = TransactionHandler(self.log_path, self.log_name, self.cas_hostname, self.cas_port)

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

        transactionID = self.transactioner.performTransaction(order)
        self.assertEqual(transactionID, 0)

    def test_invalidTransaction(self):
        """
        Tests invalid order
        :return:
        """
        order = {
            "name": "GameStart",
            "quantity": 140,
            "type": "buy"
        }

        transactionID = self.transactioner.performTransaction(order)
        self.assertEqual(transactionID, None)

    def test_invalidStock(self):
        """
        Tests invalid stock name
        :return:
        """
        order = {
            "name": "GameStop",
            "quantity": 40,
            "type": "buy"
        }

        transactionID = self.transactioner.performTransaction(order)
        self.assertEqual(transactionID, None)

    def tearDown(self) -> None:
        """
        Tear down for tests
        :return:
        """
        start_server_event.set()
        # Dummy request to close the server loop
        requests.get(f"http://{self.cas_hostname}:{self.cas_port}/lookup/BoarCo").json()
        self.transactioner = None

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        if os.path.exists(os.path.join(self.log_path, self.log_name)):
            shutil.rmtree(self.log_path)

        time.sleep(1)


if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)
