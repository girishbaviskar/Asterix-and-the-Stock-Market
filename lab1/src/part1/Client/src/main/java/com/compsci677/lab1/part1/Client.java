package com.compsci677.lab1.part1;

import java.io.*;
import java.net.Socket;
import java.time.Instant;
import java.util.Random;
import java.util.Scanner;

/**
 * Client Class for trading
 */
public class Client {

    private final String hostname;
    private final int port;

    /**
     * Constructor method for client
     * @param hostname
     * @param port
     */
    public Client(String hostname, int port) {
        this.hostname = hostname;
        this.port = port;

    }

    /**
     * Method for interactive trading. Waits for user input.
     */
    public void interactiveTrading(){
        int selectedOption;
        String stockName;
        String finalMethodCall;
        Scanner sc = new Scanner(System.in);

        while (true) {
            System.out.println("Please select one of the following options");
            System.out.println("1. Lookup a stock price \n2. Exit");
            //take user input

            try {
                selectedOption = Integer.parseInt(sc.nextLine());
            } catch (NumberFormatException e) {
                selectedOption = 2;
            }
            switch (selectedOption) {
                //lookup
                case 1:
                    System.out.println("Enter the stock name");
                    stockName = sc.nextLine();
                    System.out.println("You selected stock " + stockName);
                    finalMethodCall = "lookup " + stockName;
                    Object serverResponse = send(this.hostname, this.port, finalMethodCall);
                    System.out.println("The response from server for " + finalMethodCall + " is: " + serverResponse + "\n");
                    break;
                default:
                    sc.close();
                    System.exit(0);
            }
        }
    }

    /**
     * Method to randomly trade and measure average response times.
     *
     * @param requestCycles num of times to send the requests
     * @param stockList available list of stocks to generate requests from
     * @param loadTestingOutputFile output file to store average response times from load testing
     */
    public void automatedRandomTrading(Integer requestCycles, String[] stockList, String loadTestingOutputFile){
        Random randomGenerator = new Random();
        String chosenStockName = "";
        String methodCall= "";

        Long totalResponseTimes = 0L;
        Long requestCount=0L;
        for (int counter =0; counter < requestCycles; counter++){
            chosenStockName = stockList[randomGenerator.nextInt(stockList.length)];
            methodCall = "lookup "+ chosenStockName;
            Long methodStartTime = System.currentTimeMillis();
            Object serverResponse = send(this.hostname, this.port, methodCall);
            Long elapsedTime = System.currentTimeMillis() - methodStartTime;
            System.out.println("The response from server for " + methodCall + " is: " + serverResponse + "\n");
            totalResponseTimes+=elapsedTime;
            requestCount+=1;
        }

        Double meanResponseTime = (double)totalResponseTimes/requestCount;
        System.out.println("Finished random auto trading. Mean response time(milliseconds): "+ meanResponseTime + " for " + requestCount + " requests.");

        if (loadTestingOutputFile !=null){
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
     * Method to create a socket connection, send request, get response and close the connection
     *
     * @param hostname
     * @param port
     * @param finalMethodCall request to send to the server
     * @return
     */
    public static Object send(String hostname, int port, String finalMethodCall) {

        Socket clientSocket = null;
        ObjectInputStream requestResponseStream = null;
        DataOutputStream outputStream = null;
        Object serverResponse = null;

        //setup connection
        try {
            clientSocket = new Socket(hostname, port);
            outputStream = new DataOutputStream(clientSocket.getOutputStream());
            requestResponseStream = new ObjectInputStream(clientSocket.getInputStream());

        } catch (IOException e) {
            System.out.println(e);
        }

        try {
            outputStream.writeUTF(finalMethodCall);
            serverResponse = requestResponseStream.readObject();

        } catch (IOException | ClassNotFoundException e) {
            System.out.println(e);
        }
        //Close connection
        try {
            outputStream.close();
            assert clientSocket != null;
            clientSocket.close();
        } catch (IOException i) {
            System.out.println(i);
        }

        return serverResponse;

    }

    /**
     * Main method to run the client
     * @param args
     */
    public static void main(String[] args) {
        String hostname = (args.length < 1) ? "127.0.0.1" : args[0];
        Integer port = (args.length < 2) ? 9888 : Integer.parseInt(args[1]);
        Integer timeLimit = (args.length < 3) ? 1000: Integer.parseInt(args[2]);
        String[] stockList = {"GameStart", "FishCo", "Invalid1", "Invalid2"};

        Client client = new Client(hostname, port);

        if (System.getProperty("interactive") != null){
            client.interactiveTrading();
        }
        else {

            String loadTestingOutputFile = System.getProperty("loadTest");
            client.automatedRandomTrading(timeLimit, stockList, loadTestingOutputFile);
        }

    }
}