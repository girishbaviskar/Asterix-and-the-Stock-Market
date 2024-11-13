package com.compsci677.lab1.part1;


import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.*;

/**
 * Server Class for running a socket-based server
 */
public class Server {

    private ServerSocket server = null;

    private ConcurrentHashMap<String, ConcurrentHashMap<String, Float>> stockDatabase = null;

    private static Logger log = LogManager.getLogManager().getLogger(Logger.GLOBAL_LOGGER_NAME);

    /**
     * Constructor method for Server
     *
     * @param port     port number for the open connection
     * @param nThreads number of threads in the threadpool
     */
    public Server(int port, int nThreads, String silent) {
        log.log(Level.INFO, "Starting Server with " + nThreads + " threads");
        populateDatabase();
        ThreadPool threadPool = new ThreadPool(nThreads);
        threadPool.startThreadPool();

        try {
            server = new ServerSocket(port);
            log.log(Level.INFO, "Server Started");

            if (silent != null){
                log.setLevel(Level.OFF);
            }


            while (true) {
                Socket socket = server.accept();
                RequestRunner requestRunner = new RequestRunner(socket, this.stockDatabase);
                threadPool.addRequest(requestRunner);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Method to populate a thread-safe stock database. Uses ConcurrentHashMaps.
     */
    private void populateDatabase() {

        ConcurrentHashMap<String, Float> stock1 = new ConcurrentHashMap<String, Float>();

        stock1.put("price", (float) 15.99);

        this.stockDatabase = new ConcurrentHashMap<String, ConcurrentHashMap<String, Float>>();

        this.stockDatabase.put("FishCo", stock1);

        ConcurrentHashMap<String, Float> stock2 = new ConcurrentHashMap<String, Float>();

        stock2.put("price", (float) 12.32);

        this.stockDatabase.put("GameStart", stock2);

        log.log(Level.INFO, "Populated Stock Database");

    }

    /**
     * @param args Command line arguments.
     *             Only 1 optional argument expected (num of threads)
     *             Default value 5.
     */
    public static void main(String[] args) {

        int nThreads = (args.length < 1) ? 5 : Integer.parseInt(args[0]);
        int port = (args.length < 2) ? 9888 : Integer.parseInt(args[1]);

        Server server = new Server(port, nThreads, System.getProperty("silent"));
    }
}