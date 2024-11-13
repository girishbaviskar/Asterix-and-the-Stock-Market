import requests
def updateStockQuantity(value, changeRequest):
    """
    Function to update stock quantity and trading volume
    :param value: current value of stock
    :param changeRequest: modification to make to the value
    :return:
    """
    try:
        value["quantity"] += changeRequest["quantity"]
        value["tradingVolume"] += abs(changeRequest["quantity"])
        status = True
    except:
        status = False
    return value, status

def invalidateFrontendCache(config, stockName):
    """
    Sends request to frontend to invalidate cache
    :param config:
    :param stockName:
    :return:
    """
    requests.get(f"{config['frontend_addr']}/invalidate/{config['secret_key']}/{stockName}")