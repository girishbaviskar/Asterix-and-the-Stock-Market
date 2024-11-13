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
    stockNames = ["GameStart", "FishCo", "BoarCo", "MenhirCo", "GameStop", "DishCo", "BearCo", "PearCo", "LampCo",
                  "DampCo", "Fake1", "Invalid1", "Fake2", "Invalid2"]
    choices = [0, 1]
    orderTypes = ["buy", "sell"]
    quantityValues = [1, 2, 3]
    lookupCount = 0
    orderCount = 0
    totalLookupExecutionTime = 0
    totalOrderExecutionTime = 0
    orders = {}
    for i in range(num_requests):
        stockname = random.choices(stockNames)[0]
        startTime = time.time()

        response = requests.get(f"http://{hostname}:{port}/stocks/{stockname}")

        if display_results:
            print(response.json())

        totalLookupExecutionTime += (time.time() - startTime)
        lookupCount += 1
        chosen = random.choices(choices, weights=[1 - order_prob, order_prob])[0]
        if chosen == 1:
            # POST
            orderType = random.choices(orderTypes)[0]
            quantity = random.choices(quantityValues)[0]
            order = {
                "name": stockname,
                "quantity": quantity,
                "type": orderType
            }

            if display_results:
                print(f"Sending {order}")
            startTime = time.time()
            response = requests.post(f"http://{hostname}:{port}/orders", json=order)


            totalOrderExecutionTime += (time.time() - startTime)
            orderCount += 1

            if response.status_code == 200:
                if display_results:
                    print(response.json())
                transactionNumber = response.json()["data"]["transaction_number"]
                order["transactionID"] = transactionNumber
                orders[transactionNumber] = order

    print("======Performing order check=======")
    total_trades = len(orders)
    correct_trades = 0
    trade_verification_time = 0
    for key, value in orders.items():
        start_time = time.time()
        response = requests.get(f"http://{hostname}:{port}/orders/{key}")
        trade_verification_time += (time.time() - start_time)
        order = response.json()["data"]
        if display_results:
            print(order)
        if order == value:
            correct_trades += 1

    if total_trades > 0:

        print("======Report=======")
        print(f"Total valid trades made {total_trades}")
        print(f"Validated trades at lookup {correct_trades}")
        print(f"Percentage of lookup-validated trades {(correct_trades / total_trades) * 100}%")
        print("Avg order time", totalOrderExecutionTime / orderCount)
        print("Avg order verification time", trade_verification_time / total_trades)

    print("Total lookup count", lookupCount)
    print("Total order count", orderCount)
    print("Avg lookup time", totalLookupExecutionTime / lookupCount)


    if out_file_idx:
        if not os.path.exists("./load_test"):
            os.makedirs("./load_test")

        if not os.path.exists("./load_test/lookup"):
            os.makedirs("./load_test/lookup")

        if not os.path.exists("./load_test/orders"):
            os.makedirs("./load_test/orders")

        if not os.path.exists("./load_test/ordersVerif"):
            os.makedirs("./load_test/ordersVerif")

        with open(f"./load_test/lookup/{out_file_idx}", "w") as f:
            f.write(str(totalLookupExecutionTime / lookupCount))

        if total_trades > 0:
            with open(f"./load_test/orders/{out_file_idx}", "w") as f:
                f.write(str(totalOrderExecutionTime / orderCount))

            with open(f"./load_test/ordersVerif/{out_file_idx}", "w") as f:
                f.write(str(trade_verification_time / total_trades))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_requests", type=int, default=200)
    parser.add_argument("--out_file_idx", type=int)
    parser.add_argument("--display_results", action='store_true')
    parser.add_argument("--order_prob", type=float, default=0.5)
    parser.add_argument("--hostname", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5100)
    args = parser.parse_args()

    automatedClient(hostname=args.hostname, port=args.port, num_requests=args.num_requests,
                    out_file_idx=args.out_file_idx, display_results=args.display_results, order_prob=args.order_prob)
