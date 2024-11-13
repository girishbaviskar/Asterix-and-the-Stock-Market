package com.compsci677.lab1.part1;

import java.io.*;
import java.net.Socket;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.LogManager;
import java.util.logging.Logger;
import java.util.logging.Level;


/**
 * Runnable to run a client's request.
 * Runnables are passed to the request queue to be picked up by idle threads.
 */
public class RequestRunner implements Runnable {

    private Logger log = LogManager.getLogManager().getLogger(Logger.GLOBAL_LOGGER_NAME);

    private final Socket socket;

    private DataInputStream requestInputStream;

    private ObjectOutputStream requestResponseStream;

    private ConcurrentHashMap<String,
            ConcurrentHashMap<String, Float>> stockDatabase;

    /**
     * Constructor Method for RequestRunner Runnable
     *
     * @param socket        socket connection with the client
     * @param stockDatabase thread-safe stock database
     */
    RequestRunner(Socket socket, ConcurrentHashMap<String,
            ConcurrentHashMap<String, Float>> stockDatabase) {
        this.socket = socket;
        this.stockDatabase = stockDatabase;

        try {
            this.requestInputStream = new DataInputStream(new BufferedInputStream(this.socket.getInputStream()));
            this.requestResponseStream = new ObjectOutputStream(this.socket.getOutputStream());
        } catch (IOException e) {
            System.out.println(e);
        }
    }

    /**
     * Override Runnable's run method to custom run method to process client request
     */
    @Override
    public void run() {

        String requestContent = "";
        try {
            requestContent = requestInputStream.readUTF();
        } catch (IOException e) {
            System.out.println(e);
        }

        String[] requestContentBreakdown = requestContent.split(" ");
        String requestFunc = requestContentBreakdown[0];

        if (requestFunc.equals("lookup")) {
            this.lookup(requestContentBreakdown);
        } else {
            log.log(Level.WARNING, "Requested method not supported");
            throw new UnsupportedOperationException();
        }
    }

    /**
     * Lookup method to find a stock in the stock database. Return price if found, otherwise return -1.
     *
     * @param requestContentBreakdown Client request split by whitespace
     */
    private void lookup(String[] requestContentBreakdown) {

        String stockName = requestContentBreakdown[1];

        try {
            if (this.stockDatabase.containsKey(stockName)) {
                Float price = stockDatabase.get(stockName).get("price");
                requestResponseStream.writeObject(price);
            } else {
                requestResponseStream.writeObject(-1);
            }
        } catch (IOException e) {
            System.out.println(e);
        }

        try {
            socket.close();
            requestInputStream.close();
            requestResponseStream.close();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

}
