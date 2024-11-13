from server import CatalogServiceHandler, ThreadedServer
import logging
from database import *
from functools import partial
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    port = int(os.getenv("CAS_Port", 8081))
    hostname = os.getenv("CAS_HOSTNAME", "127.0.0.1")
    db_path = os.getenv("DB_PATH", "./db")
    db_name = os.getenv("DB_NAME", "catalog.db")
    db = connectDatabase(db_path=db_path, db_name=db_name)
    CatalogService = partial(CatalogServiceHandler, db)
    catalogServer = ThreadedServer((hostname, port), CatalogService)
    logging.info(f"Catalog Service Server started at http://{hostname}:{port}")
    try:
        catalogServer.serve_forever()
    except KeyboardInterrupt:
        pass
    catalogServer.server_close()
    logging.info(f"Catalog Service Server stopped at http://{hostname}:{port}")
