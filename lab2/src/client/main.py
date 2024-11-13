import requests
import os
import random
import time
import argparse


def automatedClient(hostname, port, num_requests, out_file_idx, display_results, order_prob):
    """
    Automated client to perform random requests
    :param hostname: frontend service hostname
    :param port: frontend service port
    :param num_requests: number of requests to send per client
    :param out_file_idx: output file idx for load testing
    :param display_results: boolean to decide whether to display responses
    :param order_prob: probability of performing and order request
    :return:
    """
    session = requests.Session()
    stockNames = ["GameStart", "FishCo", "BoarCo", "MenhirCo", "Invalid1", "Invalid2", "Invalid2"]
    choices = [0, 1]
    orderTypes = ["buy", "sell"]
    quantityValues = [1, 2, 3]
    lookupCount = 0
    orderCount = 0
    totalLookupExecutionTime = 0
    totalOrderExecutionTime = 0
    for i in range(num_requests):
        stockname = random.choices(stockNames)[0]
        startTime = time.time()
        response = session.get(f"http://{hostname}:{port}/stocks/{stockname}")

        if display_results:
            print(response.json())

        totalLookupExecutionTime += (time.time() - startTime)
        lookupCount += 1
        chosen = random.choices(choices, weights=[1-order_prob, order_prob])[0]
        if chosen == 1:
            # POST
            orderType = random.choices(orderTypes)[0]
            quantity = random.choices(quantityValues)[0]
            order = {
                "name": stockname,
                "quantity": quantity,
                "type": orderType
            }
            startTime = time.time()
            response = session.post(f"http://{hostname}:{port}/orders", json=order)

            if display_results:
                print(response.json())

            totalOrderExecutionTime += (time.time() - startTime)
            orderCount += 1
    print("total lookup count", lookupCount)
    print("total order count", orderCount)
    print("avg lookup time", totalLookupExecutionTime / lookupCount)
    print("avg order time", totalLookupExecutionTime / orderCount)

    if out_file_idx:
        if not os.path.exists("./load_test"):
            os.makedirs("./load_test")

        if not os.path.exists("./load_test/lookup"):
            os.makedirs("./load_test/lookup")

        if not os.path.exists("./load_test/orders"):
            os.makedirs("./load_test/orders")

        with open(f"./load_test/lookup/{out_file_idx}", "w") as f:
            f.write(str(totalLookupExecutionTime / lookupCount))

        with open(f"./load_test/orders/{out_file_idx}", "w") as f:
            f.write(str(totalLookupExecutionTime / orderCount))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_requests", type=int, default=200)
    parser.add_argument("--out_file_idx", type=int)
    parser.add_argument("--display_results", action='store_true')
    parser.add_argument("--order_prob", type=float, default=0.5)
    args = parser.parse_args()
    hostname = os.getenv("FES_HOSTNAME", "127.0.0.1")
    port = os.getenv("FES_PORT", 8080)

    automatedClient(hostname=hostname, port=port, num_requests=args.num_requests,
                    out_file_idx=args.out_file_idx, display_results=args.display_results, order_prob = args.order_prob)
