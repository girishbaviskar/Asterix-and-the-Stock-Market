package com.compsci677.lab1.part2;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.time.Instant;
import java.util.Random;
import java.util.logging.Level;

/**
 * Class for providing basic functionalities such as lookups and trade.
 */
public class CustomerClient extends ClientBase {


    CustomerClient(String lookupOnly, String tradeOnly) {
        super(lookupOnly, tradeOnly);
    }

    /**
     *  Method to call lookups and trade  
     *
     * @param requestCycles number of requests to be sent
     * @param loadTestingOutputFile stores the mean response time for each request
     */
    public void automatedClientDriver(Long requestCycles,  String loadTestingOutputFile) {

        Random randomGenerator = new Random();
        String chosenRequest = "";
        String chosenStockName = "";
        Long chosenNumStocks = 0L;
        TRADE_TYPE chosenTradeType = TRADE_TYPE.BUY;
        Long totalResponseTimes = 0L;
        Long requestCount = 0L;
        Long elapsedTime = 0L;
        Long methodStartTime = 0L;

        for(int counter = 0; counter < requestCycles; counter++) {

            // Choose random request;
            chosenRequest = requestOptions.get(randomGenerator.nextInt(requestOptions.size()));

            if (chosenRequest.equals("lookup")) {
                chosenStockName = stockOptions[randomGenerator.nextInt(stockOptions.length)];
                methodStartTime = System.currentTimeMillis();
                this.performLookup(chosenStockName);
                elapsedTime = System.currentTimeMillis() - methodStartTime;
            } else {
                chosenStockName = stockOptions[randomGenerator.nextInt(stockOptions.length)];
                chosenNumStocks = Long.valueOf(randomGenerator.nextInt(10));
                chosenTradeType = tradeOptions[randomGenerator.nextInt(tradeOptions.length)];
                methodStartTime = System.currentTimeMillis();
                this.performTrade(chosenStockName, chosenNumStocks, chosenTradeType);
                elapsedTime = System.currentTimeMillis() - methodStartTime;
            }
            requestCount += 1;
            totalResponseTimes += elapsedTime;
        }

        Double meanResponseTime = (double) totalResponseTimes / requestCount;
        log.log(Level.INFO, "Finished random auto trading. Mean response time(milliseconds): " + meanResponseTime + " for " + requestCount + " requests.");

        if (loadTestingOutputFile != null) {
            try {
                BufferedWriter writer = new BufferedWriter(new FileWriter(loadTestingOutputFile));
                writer.write(meanResponseTime.toString());
                writer.close();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }


    /**
     * Main function for CustomerClient
     */
    public static void main(String[] args) {
        String hostname = (args.length < 1) ? "127.0.0.1" : args[0];
        Integer port = (args.length < 2) ? 9888 : Integer.parseInt(args[1]);
        Long requestCycles = (args.length < 3) ? 1000L : Long.parseLong(args[2]);

        String lookupOnly = System.getProperty("lookupOnly");
        String tradeOnly = System.getProperty("tradeOnly");
        String loadTestingOutputFile = System.getProperty("loadTestingOutputFile");
        CustomerClient client = new CustomerClient(lookupOnly, tradeOnly);
        client.establishClient(hostname, port);

        log.log(Level.INFO, "Performing automated random trading for " + requestCycles + " seconds.");
        if (System.getProperty("silent") != null) {

            log.log(Level.INFO, "Performing trading in silent model.");
            log.setLevel(Level.OFF);
        }

        client.automatedClientDriver(requestCycles, loadTestingOutputFile);
        try {
            client.shutdownClient();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

}