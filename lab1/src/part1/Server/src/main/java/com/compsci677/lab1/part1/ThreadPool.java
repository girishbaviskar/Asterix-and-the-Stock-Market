package com.compsci677.lab1.part1;

import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

/**
 * ThreadPool implementation. Uses thread-safe custom ProducerConsumerQueue as the request queue.
 */
public class ThreadPool {

    private final int nThreads;
    private final ProducerConsumerQueue requestQueue;

    private Logger log = LogManager.getLogManager().getLogger(Logger.GLOBAL_LOGGER_NAME);

    /**
     * Constructor method for ThreadPool
     *
     * @param nThreads number of threads in the thread pool.
     */
    ThreadPool(int nThreads) {
        this.nThreads = nThreads;
        requestQueue = new ProducerConsumerQueue();
    }

    /**
     * Adding a runnable request to the request queue to be consumed by one of the idle threads.
     *
     * @param requestRunnable runnable request
     */
    public void addRequest(Runnable requestRunnable) {
        this.requestQueue.put(requestRunnable);
    }


    /**
     * Method to start the threadpool.
     *
     * @param
     */
    public void startThreadPool(){
        for (int thIdx = 0; thIdx < this.nThreads; thIdx++) {
            SinglePollingThread thread = new SinglePollingThread(requestQueue, thIdx);
            thread.start();
        }

        log.log(Level.INFO, "Created threadpool with " + nThreads + " threads");
    }
}
