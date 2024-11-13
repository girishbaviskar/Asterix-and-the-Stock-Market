# Stock Trading Application

## How to run the server

### With Docker
1. (Optional) Change the exposed port for the frontend service in ```docker-compose.yaml```  
2. Run ```docker compose build```
3. Run ```docker compose up -d --scale orderservice=3``` (You can choose the number of orderservice replicas. To increase the number of replicas more than 3, change the ```max_replicas``` parameter in ```{frontend,orderservice}/config/{frontend,orderservice}.config```)
4. To stop and teardown run ```docker compose down```

By default frontend is exposed to ```127.0.0.1:5100```.

## How to run client
```python client/main.py --num_requests=<number of request loops> --order_prob=<probability of order request 0.0-1.0> --hostname=127.0.0.1 --port=5100```

## How to run tests
We use docker to run all the tests. To run the tests:  
1. Run ```docker compose -f docker-compose-test.yaml build```  
2. Run ```docker compose -f docker-compose-test.yaml up -d```  
4. To stop and teardown run ```docker compose -f docker-compose-test.yaml down```  
Note: Rarely some test might fail if the machine does not release the ports (as each test restarts the server). Run the tests again in that case.

## Running load tests
1. Give permission to run the scripts using ```chmod u+x loadTestUtils/loadTest.sh```
2. Run ```./loadTestUtils/loadTest.sh <num request loops> <order request probability>```

## How to crash and restart an order service replica
To crash use: ```docker exec -it src-orderservice-<replica_id> bash -c 'kill -15 `ps -C gunicorn fch -o pid | head -n 1`'```  
To restart use: ```docker start src-orderservice-<replica_id>``` 

## AWS Deployment  
Install Docker on EC2 and run the service using the above steps. The service can be accessed through EC2's public DNS. Note: Change the exposed port and address for frontend service in docker compose to 0.0.0.0:5100.

## Caching
To toggle caching modify: ```{frontend,catalogservice}/config/{frontend,catalogservice}.config```