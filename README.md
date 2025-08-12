# Asterix and the Stock Bazaar

A collection of three labs for Compsci 677 (Distributed and Operating Systems), implementing a stock trading application that evolves from a monolith with custom threading to microservices with containerization, caching, replication, and fault tolerance.

## Project Overview

This project models a stock trading bazaar(Market) in the world of Asterix. It starts as a single server handling client lookups and grows into a production-style microservices system with REST APIs, persistent state, containerization, caching, replication, and fault tolerance. Along the way, it demonstrates concurrency patterns, RPC vs. REST trade-offs, service decomposition, and distributed systems concerns such as consistency and availability.

## How the project builds up

- Lab 1 — Foundations (single service):
  - Part 1: Sockets + custom thread pool. Implements a simple lookup service. Focus on concurrency primitives (producer/consumer queue, worker threads, synchronization) and request dispatch.
  - Part 2: gRPC + built-in thread pool. Adds protobuf definitions and three RPCs: Lookup, Trade, Update. Expands catalog to multiple stocks with concurrent access control.
  - Part 3: Evaluation. Load testing with multiple concurrent clients; latency vs. load; compare sockets vs. gRPC; discuss impact of thread pool sizing and synchronization.
- Lab 2 — Microservices and containers:
  - Split into frontend, catalog service, and order service.
  - Frontend exposes REST APIs: GET /stocks/<name>, POST /orders.
  - Catalog persists stock state to a file; Order service persists order log with transaction numbers.
  - Containerize each service with Docker and orchestrate with Docker Compose. Add functional tests and load tests.
- Lab 3 — Caching, replication, fault tolerance:
  - Add frontend cache with server-push invalidation from Catalog after trades.
  - Replicate Order service; select leader (highest id); followers stay consistent via replication.
  - Handle crash failures by re-selecting leader and enabling catch-up on recovery.
  - Deploy and evaluate on AWS; study latency with/without caching and under failures.

## Data and state

- Stocks: name, price, quantity (remaining), volume (traded). Persisted by Catalog in Labs 2–3 via a CSV/text file.
- Orders: number (unique, incremental), name, type (buy/sell), quantity. Persisted by Order service; replicated in Lab 3.
- Consistency mechanisms:
  - Concurrency control in single server (Lab 1) and services (Labs 2–3).
  - Cache invalidations from Catalog to Frontend (Lab 3).
  - Leader-based replication and follower catch-up for Order service (Lab 3).

## Repository Structure

- `lab1/`: Socket-based client/server and gRPC-based implementation; custom and built-in thread pools; evaluation.
- `lab2/`: Two-tier microservices (frontend, catalog, order); REST APIs; containerized with Docker and Compose; tests and load tests.
- `lab3/`: Microservices with caching, replication (leader/followers), and crash-fault tolerance; Docker; AWS deployment notes; tests and load tests.

Refer to each lab’s README for full details:

- Lab 1: `lab1/README.md`
- Lab 2: `lab2/README.md` and `lab2/src/README.md`
- Lab 3: `lab3/README.md` and `lab3/src/README.md`

## Prerequisites

- Java 11+ and Maven (for Lab 1)
- Python 3.9+ and pip (for Labs 2–3)
- Docker and Docker Compose (for Labs 2–3; optional for Lab 1)

## Quickstart

### Lab 1: Asterix and the Stock Bazaar

Two implementations of the stock bazaar:

- Part 1: Sockets + custom thread pool (Java)
- Part 2: gRPC + built-in thread pool (Java or Python; this repo contains Java with protobufs)

Key scripts and modules:

- Part 1 scripts: `lab1/src/part1/runServer.sh`, `lab1/src/part1/runClient.sh`
- Part 2 scripts: `lab1/src/part2/runServer.sh`, `lab1/src/part2/runCustomerClient.sh`, `lab1/src/part2/runUpdateClient.sh`

Typical usage (see scripts for exact args):

```bash
# Part 1
cd lab1/src/part1
./runServer.sh
./runClient.sh

# Part 2 (gRPC)
cd lab1/src/part2
./runServer.sh
./runCustomerClient.sh
./runUpdateClient.sh
```

### Lab 2: Asterix and the Microservice Stock Bazaar

Three microservices: frontend, catalogservice, orderservice; plus a simple client.

Without Docker:

```bash
cd lab2/src
pip install -r requirements.txt
# Services (each in its own terminal)
cd frontend && python main.py
cd ../catalogservice && python main.py
cd ../orderservice && python main.py
# Client
python ../client/main.py --num_requests=<loops> --order_prob=<0.0-1.0>
```

With Docker Compose:

```bash
cd lab2/src
docker compose build
docker compose up -d
# teardown
docker compose down
```

Defaults are provided via environment variables (see `lab2/src/README.md`).

### Lab 3: Replication, Caching, and Fault Tolerance

Extends Lab 2 with caching (frontend), replicated order service with leader/followers, and crash tolerance.

Run with Docker Compose (scale order replicas):

```bash
cd lab3/src
docker compose build
docker compose up -d --scale orderservice=3
# teardown
docker compose down
```

Frontend defaults to `127.0.0.1:5100`. See `lab3/src/README.md` for config toggles (e.g., caching), scaling, and AWS notes.

## Testing

- Lab 1 (JUnit):
  - Part 1 server tests: `lab1/src/part1/Server/src/test/java/ServerTest.java`
  - Run with Maven from the respective module directory (or via IDE):
    ```bash
    cd lab1/src/part1/Server
    ./mvnw test || mvn test
    ```
- Lab 2 (Dockerized tests):
  ```bash
  cd lab2/src
  docker compose -f docker-compose-tests.yaml build
  docker compose -f docker-compose-tests.yaml up -d
  docker compose -f docker-compose-tests.yaml down
  ```
- Lab 3 (Dockerized tests):
  ```bash
  cd lab3/src
  docker compose -f docker-compose-test.yaml build
  docker compose -f docker-compose-test.yaml up -d
  docker compose -f docker-compose-test.yaml down
  ```

Note: Some tests restart services; if a port is briefly unavailable, rerun the tests.

## Load Testing

- Lab 1: see `lab1/src/part1/loadTestUtils/` and `lab1/src/part2/loadTestUtils/` for scripts.
- Lab 2: `lab2/src/loadTestUtils/loadTest.sh`
  ```bash
  cd lab2/src
  chmod u+x loadTestUtils/loadTest.sh
  ./loadTestUtils/loadTest.sh <num_loops> <order_prob>
  ```
- Lab 3: `lab3/src/loadTestUtils/loadTest.sh`
  ```bash
  cd lab3/src
  chmod u+x loadTestUtils/loadTest.sh
  ./loadTestUtils/loadTest.sh <num_loops> <order_prob>
  ```

## Documentation

Each lab includes design, outputs, and evaluation docs under `labN/docs/`:

- Lab 1: `lab1/docs/`
- Lab 2: `lab2/docs/`
- Lab 3: `lab3/docs/`

For complete lab specifications and rubrics, see the respective lab READMEs and PDFs under `lab*/docs/`.

## Author

- Girish Baviskar (gbaviskar@umass.edu)
