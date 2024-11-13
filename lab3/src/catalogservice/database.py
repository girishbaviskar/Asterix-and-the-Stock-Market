import pysos
import os
import logging
from readerwriterlock import rwlock
logging.basicConfig(level=logging.INFO)


class Database:
    """
    Thread-safe key-value persistent database with reader-writer lock
    """

    def __init__(self, db_path, db_name):
        """
        Constructor method for database
        :param db_path: database path
        :param db_name: database name
        """
        self.db_path = db_path
        self.db_name = db_name
        self.db = None
        self.load_or_create()
        self.lock = rwlock.RWLockFairD()
        self.reader_lock = self.lock.gen_rlock()
        self.writer_lock = self.lock.gen_wlock()

    def load_or_create(self):
        """
        Loads an existing db or creates a new one in its absence
        :return:
        """
        if not os.path.exists(self.db_path):
            try:
                os.makedirs(self.db_path)
            except Exception as e:
                print(e)

            logging.info(f"Creating new database")

        db_full_path = os.path.join(self.db_path, self.db_name)
        self.db = pysos.Dict(db_full_path)
        logging.info(f"Database created/loaded from {db_full_path}")

    def size(self):
        """
        Returns size of the database
        :return: size
        """
        assert self.db != None, "No database available"
        return len(self.db)

    def read(self, key):
        """
        Returns the value for the given key
        :param key: key to read
        :return: None or value
        """
        assert self.db != None, "No database available"
        value = None
        with self.lock.gen_rlock():
            if key in self.db:
                value = self.db[key]

        return value

    def write(self, key, value):
        """
        Writes a key-value to the db. Replaces if the key exists already
        :param key: key to add
        :param value: value to add
        :return: boolean success or not
        """
        assert self.db != None, "No database available"

        try:
            with self.lock.gen_wlock():
                self.db[key] = value
            return True
        except:
            return False

    def updateStock(self, key, value_fn, changeRequest):
        """
        Updates the given field of stock based on value_fn function
        :param key: stockName
        :param value_fn: function to specify the field to be changed
        :param changeRequest: quantity to change
        :return: status
        """
        assert self.db != None, "No database available"
        try:
            with self.lock.gen_wlock():
                value = self.db[key]
                updated_value, status = value_fn(value, changeRequest)
                self.db[key] = updated_value
            return status
        except:
            return False

    def clear(self):
        with self.lock.gen_wlock():
            self.db.clear()

def connectDatabase(db_path, db_name):
    """
    Connects to a db instance. Populates the db if empty
    :param db_path: database path
    :param db_name: database name
    :return: db
    """
    db = Database(db_path, db_name)

    if db.size() == 0:
        populateDatabase(db)

    return db

def populateDatabase(db):
    """
    Populates the database with initial values
    :param db: database
    :return:
    """
    stockNames = ["GameStart", "FishCo", "BoarCo", "MenhirCo", "GameStop", "DishCo", "BearCo", "PearCo", "LampCo", "DampCo"]
    stockPrices = [15.99, 12.23, 11.54, 54.12, 15.99, 12.23, 11.54, 54.12, 15.99, 12.23]
    stockQuantity = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100]
    stockTradingVolume = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for idx, stock in enumerate(stockNames):
        value_dict = {"name": stock,
                      "price": stockPrices[idx],
                      "quantity": stockQuantity[idx],
                      "tradingVolume": stockTradingVolume[idx]}

        db.write(stock, value_dict)
