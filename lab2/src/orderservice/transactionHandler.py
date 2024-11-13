import os
import logging

logging.basicConfig(level=logging.INFO)
import threading
import requests
import json


class TransactionHandler:
    """
    Transaction Handler to handle order requests to the Order Service
    """
    def __init__(self, log_path, log_filename, catalogServiceHost, catalogServicePort, transactionLockTimeoutLimit=10):
        """
        Constructor method for TransactionHandler
        :param log_path:
        :param log_filename:
        :param catalogServiceHost:
        :param catalogServicePort:
        :param transactionLockTimeoutLimit:
        """
        self.log_path = log_path
        self.log_filename = log_filename
        self.catalogServiceHost = catalogServiceHost
        self.catalogServicePort = catalogServicePort
        self.transactionLockTimeoutLimit = transactionLockTimeoutLimit
        self.currentTransactionID = self.loadLastTransactionState()
        if not os.path.exists(log_path):
            try:
                os.makedirs(log_path)
            except:
                logging.error("Could not create directory for transaction logs")

        self.transactionLock = threading.Lock()

    def performTransaction(self, order):
        """
        Performs atomic thread-safe transaction i.e., only one thread has access to perform a transaction at a time
        :param order: order request JSON
        :return:
        """
        if self.transactionLock.acquire(timeout=self.transactionLockTimeoutLimit):
            try:
                transactionSuccess = False
                stockName = order["name"]
                requestSession = requests.Session()
                requestLookup = requestSession.get(
                    f"http://{self.catalogServiceHost}:{self.catalogServicePort}/lookup/{stockName}")

                if requestLookup.status_code == 200:
                    stockData = requestLookup.json()["data"]
                    updateJSON = {"name": stockName}
                    if order["type"] in ["sell", "buy"]:
                        if order["type"] == "sell":
                            updateJSON["quantity"] = order["quantity"]
                        elif order["type"] == "buy":
                            updateJSON["quantity"] = -1 * order["quantity"]
                        if stockData["quantity"] + updateJSON["quantity"] >= 0:
                            requestUpdate = requestSession.post(
                                f"http://{self.catalogServiceHost}:{self.catalogServicePort}/update", json=updateJSON)
                            if requestUpdate.status_code == 200:
                                transaction_log = {"transactionID": self.currentTransactionID, "stockName": stockName,
                                                   "type": order["type"], "quantity": order["quantity"]}
                                with open(os.path.join(self.log_path, self.log_filename), "a") as log:
                                    log.write(json.dumps(transaction_log) + "\n")

                                self.currentTransactionID +=1
                                transactionSuccess = True
                requestSession.close()
                if transactionSuccess == True:
                    return transaction_log["transactionID"]
                else:
                    return None

            finally:
                self.transactionLock.release()

        return None

    def loadLastTransactionState(self):
        """
        Method to get the last transaction ID from the transaction log in case of service restart. Assists in maintaining
        transaction ID across restarts
        :return:
        """
        if not os.path.exists(os.path.join(self.log_path, self.log_filename)):
            return 0
        else:
            logFile = open(os.path.join(self.log_path, self.log_filename), 'r')
            logLines = logFile.readlines()
            return len(logLines)
