package com.compsci677.lab1.part2;

import io.grpc.stub.StreamObserver;

public class TradingServiceImpl extends TradingServiceGrpc.TradingServiceImplBase {

    private final StockDatabase stockDatabase;

    TradingServiceImpl(StockDatabase stockDatabase) {
        super();
        this.stockDatabase = stockDatabase;
    }

    /**Implements gRPC lookup function */
    @Override
    public void lookup(LookupRequest request, StreamObserver<LookupResponse> responseObserver) {
        String stockName = request.getStockName();
        LookupResponse lookupResponse = this.stockDatabase.lookupDatabase(stockName);
        responseObserver.onNext(lookupResponse);
        responseObserver.onCompleted();
    }

    /**Implements gRPC trade function */
    @Override
    public void trade(TradeRequest request, StreamObserver<TradeResponse> responseObserver) {
        String stockName = request.getStockName();
        Long numStocks = request.getNumStocks();
        TRADE_TYPE tradeType = request.getTradeType();
        TradeResponse tradeResponse = this.stockDatabase.tradeDatabase(stockName, numStocks, tradeType);
        responseObserver.onNext(tradeResponse);
        responseObserver.onCompleted();
    }

    /**Implements gRPC update function */
    @Override
    public void update(UpdateRequest request, StreamObserver<UpdateResponse> responseObserver) {
        String stockName = request.getStockName();
        Float price = request.getPrice();
        UpdateResponse updateResponse = this.stockDatabase.updateDatabase(stockName, price);
        responseObserver.onNext(updateResponse);
        responseObserver.onCompleted();
    }
}
