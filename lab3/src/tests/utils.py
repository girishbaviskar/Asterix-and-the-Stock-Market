import requests
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

def cleanState(catalog_url, order_url, secret_key):
    clear_catalog = requests.get(f"{catalog_url}/clearDB/{secret_key}")
    clear_order = requests.get(f"{order_url}/clearDB/{secret_key}")