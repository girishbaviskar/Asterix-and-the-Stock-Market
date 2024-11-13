from server import OrderServiceHandler, ThreadedServer
import logging
from transactionHandler import *
from functools import partial
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    catalogServicePort = int(os.getenv("CAS_Port", 8081))
    catalogServiceHostname = os.getenv("CAS_HOSTNAME", "127.0.0.1")
    orderServiceHostname = os.getenv("ORS_HOSTNAME", "127.0.0.1")
    orderServicePort = int(os.getenv("ORS_PORT", 8082))
    log_path = os.getenv("LOG_PATH", "./log")
    log_name = os.getenv("LOG_NAME", "transactions.log")
    transactionHandler = TransactionHandler(log_path=log_path, log_filename=log_name,
                                            catalogServiceHost=catalogServiceHostname,
                                            catalogServicePort=catalogServicePort)
    orderService = partial(OrderServiceHandler, transactionHandler)
    orderServer = ThreadedServer((orderServiceHostname, orderServicePort), orderService)
    logging.info(f"Order Service Server started at http://{orderServiceHostname}:{orderServicePort}")
    try:
        orderServer.serve_forever()
    except KeyboardInterrupt:
        pass
    orderServer.server_close()
    logging.info(f"Catalog Service Server stopped at http://{orderServiceHostname}:{orderServicePort}")
