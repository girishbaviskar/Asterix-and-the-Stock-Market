# Part 2 gRPC Trading Application

## How to run  
Note: If the scripts return Permission Denied error use ``` chmod u+x <script>.sh ``` before running.

In the following scripts replace ```<build tool>``` with ```mvn``` if you have maven installed, otherwise replace with ```./mvnw``` (EdLab).

Running the server:
```
./runServer.sh <build tool> <port> <nThreads>
```

Running the customer client:
```
./runCustomerClient.sh <build tool> <hostname> <port> <numRequestToSend>
```

Running the updating client:
```
./runUpdateClient.sh <build tool> <hostname> <port> <timeLimit>
```

Running the load tests:

1. lookUpOnly:

```
./loadTestUtils/loadTestLookup.sh <build tool> <hostname> <port>
```
2. tradeOnly
```
./loadTestUtils/loadTestTrade.sh <build tool> <hostname> <port>
```

The load test result will be saved in ```./loadTestResult```.  

You can change the number of parallel clients and numRequests per client by modifying  ```loadTest.sh``` by:
```
.
.
for run in {1..<numClients>};
do
$1 exec:java -pl Client -Dexec.mainClass=com.compsci677.lab1.part2.CustomerClient -DlookupOnly -DloadTestingOutputFile="loadTestResult/loadRes$run" -Dexec.args="$2 $3 <numRequestToSend>" &
done
.
.
```

To run client on local machine and server on Edlab, you can use ssh tunneling (As EdLab is not able to run many parallel clients):
E.g., server running on elnux1 port 9888.
```
ssh <username>@elnux.cs.umass.edu -L 9888:elnux1:9888
```

