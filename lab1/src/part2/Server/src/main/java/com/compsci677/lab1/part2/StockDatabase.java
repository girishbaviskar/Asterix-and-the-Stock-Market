package com.compsci677.lab1.part2;

import java.util.concurrent.ConcurrentHashMap;
/**
 * Class to handle all stock database operations like populating on start, price lookup, trade and update
 */
public class StockDatabase {

    private final ConcurrentHashMap<String, ConcurrentHashMap<String, Object>> stockData;

    StockDatabase() {
        this.stockData = new ConcurrentHashMap<String, ConcurrentHashMap<String, Object>>();
    }

    /**
     *  This method populates the database for the first time with names, prices and trade volume limit
     * @param stocks String list with stock names to be inserted
     * @param prices list of stock prices to assigned to each stock
     * @param tradingVolLimit list of trading volume limit
     */
    public void populateDatabase(String[] stocks, Float[] prices, Long[] tradingVolLimit) {
        assert stocks.length == prices.length;
        Long initialTradingVol = 0L;
        for (int stock_idx = 0; stock_idx < stocks.length; stock_idx++) {
            ConcurrentHashMap<String, Object> stock = new ConcurrentHashMap<String, Object>();
            stock.put("price", (Float) prices[stock_idx]);
            stock.put("tradingVolume", initialTradingVol);
            stock.put("tradingVolumeLimit", tradingVolLimit[stock_idx]);
            this.stockData.put(stocks[stock_idx], stock);
        }

    }

    /**
     * This method looksup the price of a given stock and returns it along with other information like trading volume and trading status
     * @param stockName stock name to lookup
     * 
     * @return LookupResponse
     */
    public LookupResponse lookupDatabase(String stockName) {
        LookupResponse lookupResponse = null;
        if (this.stockData.containsKey(stockName)) {
            Float price = (Float) this.stockData.get(stockName).get("price");
            Long tradingVol = (Long) this.stockData.get(stockName).get("tradingVolume");
            Long tradingVolumeLimit = (Long) this.stockData.get(stockName).get("tradingVolumeLimit");


            if (tradingVol < tradingVolumeLimit) {
                lookupResponse = LookupResponse
                        .newBuilder()
                        .setPrice(price)
                        .setTradingVolume(tradingVol)
                        .setStatus(REQUEST_STATUS.SUCCESSFUL)
                        .build();
            } else {
                lookupResponse = LookupResponse
                        .newBuilder()
                        .setPrice(0)
                        .setTradingVolume(0)
                        .setStatus(REQUEST_STATUS.TRADING_SUSPENDED)
                        .build();
            }
        } else {
            lookupResponse = LookupResponse
                    .newBuilder()
                    .setPrice(-1)
                    .setTradingVolume(-1)
                    .setStatus(REQUEST_STATUS.INVALID_STOCK_NAME)
                    .build();

        }

        return lookupResponse;
    }

    /**
     * This method performs the trade operation, updates trading volume of the stock if successful
     * @param stockName stock name to trade
     * @param numStocks number of stocks to trade of the above stock
     * @param tradeType type of trade whether Buy or Sell
     * 
     * @return TradeResponse
     */
    public TradeResponse tradeDatabase(String stockName, Long numStocks, TRADE_TYPE tradeType) {
        TradeResponse tradeResponse = null;
        if (!this.stockData.containsKey(stockName)) {
            tradeResponse = TradeResponse.newBuilder()
                    .setStatus(REQUEST_STATUS.INVALID_STOCK_NAME)
                    .build();
        } else {
            Long tradingVol = (Long) this.stockData.get(stockName).get("tradingVolume");
            Long tradingVolumeLimit = (Long) this.stockData.get(stockName).get("tradingVolumeLimit");

            if (tradingVol + numStocks > tradingVolumeLimit) {
                tradeResponse = TradeResponse.newBuilder()
                        .setStatus(REQUEST_STATUS.TRADING_SUSPENDED)
                        .build();
            } else {
                this.stockData.get(stockName).put("tradingVolume", tradingVol + numStocks);
                tradeResponse = TradeResponse.newBuilder()
                        .setStatus(REQUEST_STATUS.SUCCESSFUL)
                        .build();
            }
        }

        return tradeResponse;
    }

    /**
     * This method updates price of a given stock if found in the database
     * @param stockName stock name of the stock to update the price
     * @param updatedPrice new price of the stock
     * 
     * @return UpdateResponse
     */
    public UpdateResponse updateDatabase(String stockName, Float updatedPrice) {
        UpdateResponse updateResponse = null;

        if (updatedPrice < 0) {
            updateResponse = updateResponse.newBuilder().setStatus(REQUEST_STATUS.INVALID_PRICE).build();
        } else if (!stockData.containsKey(stockName)) {
            updateResponse = updateResponse.newBuilder().setStatus(REQUEST_STATUS.INVALID_STOCK_NAME).build();
        } else {
            Float price = (Float) this.stockData.get(stockName).get("price");
            this.stockData.get(stockName).put("price", updatedPrice);
            updateResponse = updateResponse.newBuilder().setStatus(REQUEST_STATUS.SUCCESSFUL).build();
        }

        return updateResponse;
    }


}
