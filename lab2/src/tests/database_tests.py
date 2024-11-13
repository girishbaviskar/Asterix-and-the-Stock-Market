from catalogservice import database
import unittest
import os
import shutil


class DatabaseTests(unittest.TestCase):
    """
    Defines test cases for the database
    """

    def setUp(self) -> None:
        """
        Setup method for tests
        :return:
        """
        self.db_path = "./test_db"
        self.db_name = "test_db.db"

        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        self.db = database.Database(self.db_path, self.db_name)

    def test_init(self):
        """
        Tests db initialization
        :return:
        """
        self.assertTrue(os.path.exists(os.path.join(self.db_path, self.db_name)))
        self.assertEqual(dict(self.db.db), {})

    def test_populate(self):
        """
        Tests populating the database
        :return:
        """
        database.populateDatabase(self.db)
        expected_output = {'GameStart': {'name': 'GameStart', 'price': 15.99, 'quantity': 100, 'tradingVolume': 0},
                           'FishCo': {'name': 'FishCo', 'price': 12.23, 'quantity': 100, 'tradingVolume': 0},
                           'BoarCo': {'name': 'BoarCo', 'price': 11.54, 'quantity': 100, 'tradingVolume': 0},
                           'MenhirCo': {'name': 'MenhirCo', 'price': 54.12, 'quantity': 100, 'tradingVolume': 0}}

        self.assertEqual(dict(self.db.db), expected_output)

    def test_size(self):
        """
        Tests if the size method gives the correct db size
        :return:
        """
        database.populateDatabase(self.db)
        self.assertEqual(self.db.size(), 4)

    def test_read(self):
        """
        Tests read method
        :return:
        """
        database.populateDatabase(self.db)
        read_value = self.db.read("BoarCo")
        expected_value = {'name': 'BoarCo', 'price': 11.54, 'quantity': 100, 'tradingVolume': 0}
        self.assertEqual(read_value, expected_value)

    def test_write(self):
        """
        Tests db write method
        :return:
        """
        database.populateDatabase(self.db)
        status = self.db.write("BoarCo", {'name': 'BoarGo', 'price': 11.54, 'quantity': 90, 'tradingVolume': 0})
        self.assertTrue(status)
        read_value = self.db.read("BoarCo")
        expected_value = {'name': 'BoarGo', 'price': 11.54, 'quantity': 90, 'tradingVolume': 0}
        self.assertEqual(read_value, expected_value)

    def test_updateStock(self):
        """
        Tests db updateStock method (used for orders)
        :return:
        """

        def value_fn(value, changeRequest):
            value["quantity"] += changeRequest
            return value, True

        database.populateDatabase(self.db)
        status = self.db.updateStock("BoarCo", value_fn, 50)
        self.assertTrue(status)
        after_value = self.db.read("BoarCo")
        expected_value = {'name': 'BoarCo', 'price': 11.54, 'quantity': 150, 'tradingVolume': 0}
        self.assertEqual(after_value, expected_value)

    def tearDown(self) -> None:
        """
        Tear down for tests
        :return:
        """
        self.db.db._file.close()
        if os.path.exists(os.path.join(self.db_path, self.db_name)):
            shutil.rmtree(self.db_path)

        self.db_path = None
        self.db_name = None


if __name__ == "__main__":
    unittest.main(warnings='ignore', verbosity=2)
