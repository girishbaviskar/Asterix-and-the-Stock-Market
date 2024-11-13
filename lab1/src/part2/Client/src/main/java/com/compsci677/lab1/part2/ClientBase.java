package com.compsci677.lab1.part2;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;
import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

/**
 * Class for providing basic functionalities such as creating, closing connections and handlling requests.
 */
public class ClientBase {

    public static Logger log = LogManager.getLogManager().getLogger(Logger.GLOBAL_LOGGER_NAME);
    private TradingServiceGrpc.TradingServiceBlockingStub blockingStub;

    protected ArrayList<String> requestOptions = new ArrayList<String>();
    protected String[] stockOptions = {"GameStart", "FishCo", "MenhirCo", "BoarCo", "Invalid1", "Invalid2"};

    protected TRADE_TYPE[] tradeOptions = {TRADE_TYPE.BUY, TRADE_TYPE.SELL};
    private ManagedChannel channel;

    public ClientBase() {

    }

    /**
     * Constructor method for the ClientBase
     *
     * @param lookuponly true if only running lookup 
     * @param tradeonly   true if only running trade
     */
    public ClientBase(String lookupOnly, String tradeOnly) {

        if (lookupOnly != null) {
            log.log(Level.INFO, "Only performing lookup");
            requestOptions.add("lookup");
        } else if (tradeOnly != null) {
            log.log(Level.INFO, "Only performing trade");
            requestOptions.add("trade");
        } else {
            requestOptions.add("lookup");
            requestOptions.add("trade");
        }

    }

    /**
     * Method to setup connection
     *
     * @param hostname client hostname
     * @param port     port number for service running
     */
    public void establishClient(String hostname, int port) {
        channel = ManagedChannelBuilder.forAddress(hostname, port).usePlaintext().build();
        blockingStub = TradingServiceGrpc.newBlockingStub(channel);
        log.log(Level.INFO, "Client Established.");
    }


    /**
     * Method to query stock prices from the server
     *
     * @param stockName name of the stock to query the price
     */
    public void performLookup(String stockName) {
        LookupRequest lookupRequest = LookupRequest.newBuilder()
                .setStockName(stockName)
                .build();

        LookupResponse lookupResponse = blockingStub.lookup(lookupRequest);
        REQUEST_STATUS responseStatus = lookupResponse.getStatus();
        Float responsePrice = lookupResponse.getPrice();
        Long responseTradingVol = lookupResponse.getTradingVolume();

        String outputString = "lookup(" + stockName + ") response > Status: " +
                responseStatus + " Status Code: " + responseStatus.getNumber() +
                " Price: " + responsePrice + " Trading Volume: " + responseTradingVol;
        log.log(Level.INFO, outputString);
    }

    /**
     * Method to perform the trade on server 
     *
     * @param stockName name of the stock to trade
     * @param numStocks number of stocks to trade
     * @param tradeType type of trade, sell or buy         
     */
    public void performTrade(String stockName, Long numStocks, TRADE_TYPE tradeType) {
        TradeRequest tradeRequest = TradeRequest.newBuilder()
                .setStockName(stockName)
                .setNumStocks(numStocks)
                .setTradeType(tradeType)
                .build();

        TradeResponse tradeResponse = blockingStub.trade(tradeRequest);

        REQUEST_STATUS responseStatus = tradeResponse.getStatus();
        String outputString = "trade(" + stockName + "," + numStocks + "," + tradeType + ") response > Status: " +
                responseStatus + " Status Code: " + responseStatus.getNumber();
        log.log(Level.INFO, outputString);
    }

    /**
     * Method to update price of the stock
     *
     * @param stockName name of the stock to trade
     * @param updatedPrice new price to be updated with
     */
    public void performUpdate(String stockName, Float updatedPrice) {
        UpdateRequest updateRequest = UpdateRequest.newBuilder()
                .setStockName(stockName)
                .setPrice(updatedPrice)
                .build();

        UpdateResponse updateResponse = blockingStub.update(updateRequest);
        REQUEST_STATUS responseStatus = updateResponse.getStatus();
        String outputString = "update(" + stockName + "," + updatedPrice + ") response > Status: " +
                responseStatus + " Status Code: " + responseStatus.getNumber();
        log.log(Level.INFO, outputString);
    }

    /**
     * Closes the connection with server
     *
     * 
     */
    public void shutdownClient() throws InterruptedException {
        channel.shutdownNow().awaitTermination(3, TimeUnit.SECONDS);
        log.log(Level.INFO, "Client shutdown");
    }

}
