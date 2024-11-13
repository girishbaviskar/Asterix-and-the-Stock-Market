import os
import unittest
import glob
from utils import populateDatabase, cleanState
import requests



class CatalogTests(unittest.TestCase):
    """
    Tests for frontend
    """

    def setUp(self) -> None:
        self.frontend_url = "http://src-frontend-1:9999"
        self.catalog_url = "http://src-catalogservice-1:9999"
        self.order_url = "http://src-orderservice-1:9999"
        self.secret_key = "BAD_SECRET_KEY"

        cleanState(catalog_url=self.catalog_url, order_url=self.order_url, secret_key=self.secret_key)

    def test_lookup(self):
        """
        Tests lookup request
        :return:
        """
        response_value = requests.get(f"{self.catalog_url}/lookup/BoarCo").json()
        expected_value = {'data': {'name': 'BoarCo', 'price': 11.54, 'quantity': 100}}
        self.assertEqual(expected_value, response_value)

    def test_invalidLookup(self):
        """
        Tests an invalid lookup request
        :return:
        """
        response_value = requests.get(f"{self.catalog_url}/lookup/Boarpo").json()
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
        changeRequest = {"name": "BoarCo", "quantity": -10}
        response = requests.post(f"{self.catalog_url}/update", json=changeRequest)
        self.assertEqual(response.status_code, 200)

    def test_invalidUpdate(self):
        """
        Tests invalid stock update (order)
        :return:
        """
        changeRequest = {"name": "BoarPo", "quantity": -10}
        response = requests.post(f"{self.catalog_url}/update", json=changeRequest)
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)