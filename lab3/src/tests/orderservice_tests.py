import os
import unittest
import glob
from utils import populateDatabase, cleanState
import requests


class OrderTests(unittest.TestCase):
    """
    Tests for frontend
    """

    def setUp(self) -> None:
        self.frontend_url = "http://src-frontend-1:9999"
        self.catalog_url = "http://src-catalogservice-1:9999"
        self.order_url = "http://src-orderservice-1:9999"
        self.secret_key = "BAD_SECRET_KEY"

        cleanState(catalog_url=self.catalog_url, order_url=self.order_url, secret_key=self.secret_key)

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
        response = requests.post(f"{self.order_url}/orders", json=order)
        expected_response = {'data': {'transaction_number': 0}}
        self.assertEqual(response.json(), expected_response)

    def test_validTransactionAndOrderLookup(self):
        """
        Tests valid order and order lookup
        :return:
        """
        order = {
            "name": "GameStart",
            "quantity": 1,
            "type": "sell"
        }
        response = requests.post(f"{self.order_url}/orders", json=order)
        expected_response = {'data': {'transaction_number': 0}}
        self.assertEqual(response.json(), expected_response)
        response = requests.get(f"{self.order_url}/orders/0")
        expected_response = {'data': {"transactionID": 0, "name": "GameStart", "quantity": 1, "type": "sell"}}
        self.assertEqual(response.json(), expected_response)

    def test_invalidOrderLookup(self):
        """
        Tests valid invalid order lookup
        :return:
        """
        response = requests.get(f"{self.order_url}/orders/99")
        expected_response = {
            "error": {
                "code": 404,
                "message": "order not found"
            }
        }
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
        response = requests.post(f"{self.order_url}/orders", json=order)
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
        response = requests.post(f"{self.order_url}/orders", json=order)
        expected_response = {
            "error": {
                "code": 404,
                "message": "transaction unsuccessful"
            }
        }
        self.assertEqual(response.json(), expected_response)


if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)
