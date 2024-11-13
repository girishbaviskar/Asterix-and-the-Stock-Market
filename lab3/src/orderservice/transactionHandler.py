import os
import logging

logging.basicConfig(level=logging.INFO)
import threading
import requests
import json
from utils import send_sync

class TransactionHandler:
    """
    Transaction Handler to handle order requests to the Order Service
    """
    def __init__(self, config, db, transactionLockTimeoutLimit=1):
        """
        Constructor method for TransactionHandler
        :param log_path:
        :param log_filename:
        :param catalogServiceHost:
        :param catalogServicePort:
        :param transactionLockTimeoutLimit:
        """
        self.catalogServiceAddr = config["catalog_service_addr"]
        self.transactionLockTimeoutLimit = transactionLockTimeoutLimit
        self.currentTransactionID = self.loadLastTransactionState(db) + 1

        self.transactionLock = threading.Lock()

    def performTransaction(self, order, db, config):
        """
        Performs atomic thread-safe transaction i.e., only one thread has access to perform a transaction at a time
        :param order: order request JSON
        :return:
        """
        if self.transactionLock.acquire(timeout=self.transactionLockTimeoutLimit):
            try:
                transactionSuccess = False
                stockName = order["name"]
                requestLookup = requests.get(
                    f"{self.catalogServiceAddr}/lookup/{stockName}")
                if requestLookup.status_code == 200:
                    stockData = requestLookup.json()["data"]
                    updateJSON = {"name": stockName}
                    if order["type"] in ["sell", "buy"]:
                        if order["type"] == "sell":
                            updateJSON["quantity"] = order["quantity"]
                        elif order["type"] == "buy":
                            updateJSON["quantity"] = -1 * order["quantity"]
                        if stockData["quantity"] + updateJSON["quantity"] >= 0:
                            requestUpdate = requests.post(
                                f"{self.catalogServiceAddr}/update", json=updateJSON)
                            if requestUpdate.status_code == 200:
                                transaction_log = {"transactionID": self.currentTransactionID, "name": stockName,
                                                   "type": order["type"], "quantity": order["quantity"]}
                                db.write(self.currentTransactionID, transaction_log)
                                send_sync(config["orderservice_config"], transaction_log,
                                          config["leader_addr"])
                                self.currentTransactionID +=1
                                transactionSuccess = True
                if transactionSuccess == True:
                    return transaction_log
                else:
                    return None

            finally:
                self.transactionLock.release()
        return None

    def loadLastTransactionState(self, db):
        """
        Method to get the last transaction ID from the transaction log in case of service restart. Assists in maintaining
        transaction ID across restarts
        :return:
        """
        return db.get_max_key()

    def updateLastTransactionState(self, db):
        """
        Updates last transaction ID
        :param db:
        :return:
        """
        self.currentTransactionID = self.loadLastTransactionState(db) + 1