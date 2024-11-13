# Stock Trading Application

## How to run the server

### Without Docker
Install the requirements in ```requirements.txt``` using ```pip install -r requirements.txt```   
You need to set the following environment variables prior to running the application:  
Frontend service: FES_PORT, FES_HOSTNAME  
Catalog service: CAS_PORT, CAS_HOSTNAME, DB_PATH, DB_NAME  
Order service: ORS PORT, ORS_HOSTNAME, LOG_PATH, LOG_NAME  
If the environment variables are not set, default values will be used.

To run the frontend service:  
```
cd frontend
python main.py
```

To run the catalog service:
```
cd catalogservice
python main.py
```

To run the order service:
```
cd orderservice
python main.py
```

By default frontend service is bind to ```127.0.0.1:8080```

### With Docker
1. (Optional) Change the exposed port for the frontend service in ```docker-compose.yaml```  
2. Run ```docker compose build```
3. Run ```docker compose up -d```
4. To stop and teardown run ```docker compose down```


## How to run client
```python client/main.py --num_requests=<number of request loops> --order_prob=<probability of order request 0.0-1.0>```

## How to run tests
We use docker to run all the tests. To run the tests:  
1. Run ```docker compose -f docker-compose-tests.yaml build```  
2. Run ```docker compose -f docker-compose-tests.yaml up -d```  
4. To stop and teardown run ```docker compose -f docker-compose-tests.yaml down```
Note: Rarely some test might fail if the machine does not release the ports (as each test restarts the server). Run the tests again in that case.

## Running load tests
1. Give permission to run the scripts using ```chmod u+x loadTestUtils/loadTest.sh```
2. Run ```./loadTestUtils/loadTest.sh <num request loops> <order request probability>```
