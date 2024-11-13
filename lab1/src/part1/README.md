# Part 1: Trading Application with Threadpool

# Requirements
```
java 11
maven (Optional)
```
## How to run  
Note: If the scripts return Permission Denied error use ``` chmod u+x <script>.sh ``` before running.

In the following scripts replace ```<build tool>``` with ```mvn``` if you have maven installed, otherwise replace with ```./mvnw``` (EdLab).

Running the server:
```
./runServer.sh <build tool> <nThreads> <port>
```

Running the client:
```
./runClient.sh <build tool> <hostname> <port> <numRequestToSend>
```

Running the load tests:

```
./loadTestUtils/loadTest.sh <build tool> <hostname> <port>
```
The load test result will be saved in ```./loadTestResult```.  

You can change the number of parallel clients and numRequests per client by modifying  ```loadTest.sh``` by:
```
.
.
for run in {1..<numParallelClients>};
do
$1 exec:java -pl Client -Dexec.mainClass=com.compsci677.lab1.part1.Client -DloadTest="loadTestResult/loadRes$run" -Dexec.args="$2 $3 <numRequests>" &
done
wait
.
.
```

To run client on local machine and server on Edlab, you can use ssh tunneling (As EdLab is not able to run many parallel clients):
E.g., server running on elnux1 port 9888.
```
ssh <username>@elnux.cs.umass.edu -L 9888:elnux1:9888
```

