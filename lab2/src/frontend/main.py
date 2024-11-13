import os
from server import FrontEndHandler, ThreadedServer
import logging
from functools import partial
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    port = int(os.getenv("FES_PORT", 8080))
    hostname = os.getenv("FES_HOSTNAME", "127.0.0.1")
    catlogServiceHostname = os.getenv("CAS_HOSTNAME", "127.0.0.1")
    catlogServicePort = int(os.getenv("CAS_PORT", 8081))
    orderServiceHostname = os.getenv("ORS_HOSTNAME", "127.0.0.1")
    orderServicePort = int(os.getenv("ORS_PORT", 8082))
    FrontEndService = partial(FrontEndHandler, catlogServiceHostname, catlogServicePort, orderServiceHostname, orderServicePort)
    frontendServer = ThreadedServer((hostname, port), FrontEndService)
    logging.info(f"Frontend Server started at http://{hostname}:{port}")
    try:
        frontendServer.serve_forever()
    except KeyboardInterrupt:
        pass
    frontendServer.server_close()
    logging.info(f"Frontend Server stopped at http://{hostname}:{port}")
