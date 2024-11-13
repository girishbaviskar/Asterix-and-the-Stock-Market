package com.compsci677.lab1.part2;

import java.time.Instant;
import java.util.Random;
import java.util.logging.Level;
/**
 * Class for providing basic functionality of updating the stock price
 */
public class UpdatingClient extends ClientBase {

    public UpdatingClient() {
        super();
    }

    /**
     * This method handles random update calls to the server
     */
    public void automatedUpdateDriver(Long timeLimit, Float min, Float max) throws InterruptedException {
        Random randomGenerator = new Random();
        String chosenStockName = "";
        Float chosenUpdatePrice = 0.0F;
        Integer sleepTimeMillis = 0;

        long startTime = Instant.now().getEpochSecond();
        long currentTime = startTime;

        while (currentTime - startTime < timeLimit) {

            chosenStockName = stockOptions[randomGenerator.nextInt(stockOptions.length)];
            chosenUpdatePrice = randomGenerator.nextFloat() * (max - min) + min;
            this.performUpdate(chosenStockName, chosenUpdatePrice);
            sleepTimeMillis = randomGenerator.nextInt(1000);
            Thread.sleep(sleepTimeMillis);
            currentTime = Instant.now().getEpochSecond();
        }
    }

    public static void main(String[] args) {
        String hostname = (args.length < 1) ? "127.0.0.1" : args[0];
        Integer port = (args.length < 2) ? 9888 : Integer.parseInt(args[1]);
        Long timeLimit = (args.length < 3) ? 10L : Long.parseLong(args[2]);
        Float minPrice = -10.0F;
        Float maxPrice = 50.0F;

        UpdatingClient client = new UpdatingClient();
        client.establishClient(hostname, port);

        log.log(Level.INFO, "Performing automated random updating for " + timeLimit + " seconds.");
        if (System.getProperty("silent") != null){

            log.log(Level.INFO, "Performing updating in silent model.");
            log.setLevel(Level.OFF);
        }
        try {
            client.automatedUpdateDriver(timeLimit, minPrice, maxPrice);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        try {
            client.shutdownClient();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

}
