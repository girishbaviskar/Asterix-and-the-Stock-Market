package com.compsci677.lab1.part2;

import io.grpc.Server;
import io.grpc.ServerBuilder;

import java.io.IOException;
import java.util.concurrent.*;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

/* 
 * Class to start the server
*/
public class TradingServer {


    public static void main(String[] args) throws IOException, InterruptedException {
        Integer port = (args.length < 1) ? 9888 : Integer.parseInt(args[0]);
        Integer threadPoolLimit = (args.length < 2) ? 10 : Integer.parseInt(args[1]);

        Logger log = LogManager.getLogManager().getLogger(Logger.GLOBAL_LOGGER_NAME);
        String[] stocks = {"FishCo", "GameStart", "BoarCo", "MenhirCo"};
        Float[] stockPrices = {11.5F, 14.2F, 22.5F, 15.6F};
        Long[] tradingLimits = {110000L, 30000L, 120000L, 12000L};

        StockDatabase stockDatabase = new StockDatabase();
        stockDatabase.populateDatabase(stocks, stockPrices, tradingLimits);
        ThreadPoolExecutor dynamicThreadPool = new ThreadPoolExecutor(0, threadPoolLimit, 100L, TimeUnit.SECONDS, new SynchronousQueue<>());
        log.log(Level.INFO, "Creating dynamic threadpool with " + threadPoolLimit + " maximum threads");

        Server server = ServerBuilder.forPort(port)
                .addService(new TradingServiceImpl(stockDatabase))
                .executor(dynamicThreadPool)
                .build();

        server.start();

        log.log(Level.INFO, "Server started.");

        server.awaitTermination();
    }
}