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
import threading

start_server_event = threading.Event()


def startServer(cas_hostname, cas_port, db_path, db_name):
    """
    Starts catalog service server
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


class CatalogServiceTest(unittest.TestCase):
    """
    Defines test cases for the Catalog Service
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
        start_server_event.clear()

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        self.serverProc = threading.Thread(target=startServer,
                                           args=(self.cas_hostname, self.cas_port, self.db_path, self.db_name))
        self.serverProc.start()
        time.sleep(2)

    def test_lookup(self):
        """
        Tests lookup
        :return:
        """
        time.sleep(2)
        response_value = requests.get(f"http://{self.cas_hostname}:{self.cas_port}/lookup/BoarCo").json()
        expected_value = {'data': {'name': 'BoarCo', 'price': 11.54, 'quantity': 100}}
        self.assertEqual(expected_value, response_value)

    def test_invalidLookup(self):
        """
        Tests invalid lookup
        :return:
        """
        time.sleep(2)
        response_value = requests.get(f"http://{self.cas_hostname}:{self.cas_port}/lookup/Boarpo").json()
        expected_value = {
            "error": {
                "code": 404,
                "message": "stock not found"
            }
        }
        self.assertEqual(expected_value, response_value)

    def test_update(self):
        """
        Tests stock update (order)
        :return:
        """
        time.sleep(2)
        changeRequest = {"name": "BoarCo", "quantity": -10}
        response = requests.post(f"http://{self.cas_hostname}:{self.cas_port}/update", json=changeRequest)
        self.assertEqual(response.status_code, 200)

    def test_invalidUpdate(self):
        """
        Tests invalid stock update (order)
        :return:
        """
        time.sleep(2)
        changeRequest = {"name": "BoarPo", "quantity": -10}
        response = requests.post(f"http://{self.cas_hostname}:{self.cas_port}/update", json=changeRequest)
        self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:
        """
        Test tear down
        :return:
        """
        start_server_event.set()
        # Dummy request to close the server loop
        requests.get(f"http://{self.cas_hostname}:{self.cas_port}/lookup/BoarCo").json()

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        time.sleep(1)


if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)
