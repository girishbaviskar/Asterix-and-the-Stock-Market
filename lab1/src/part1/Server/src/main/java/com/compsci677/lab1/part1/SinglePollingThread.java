package com.compsci677.lab1.part1;

import java.util.logging.Level;
import java.util.logging.LogManager;
import java.util.logging.Logger;

/**
 * Single worker thread which waits until a runnable is ready to be consumed in the request queue.
 * Act as threads in the thread pool.
 */
public class SinglePollingThread extends Thread {

    private ProducerConsumerQueue requestQueue;
    private final int id;

    private Logger log = LogManager.getLogManager().getLogger(Logger.GLOBAL_LOGGER_NAME);

    /**
     * Constructor method for the SinglePollingThread
     *
     * @param requestQueue request queue with runnables from the thread pool
     * @param id           id of the thread. Used for debugging or logging purposes.
     */
    SinglePollingThread(ProducerConsumerQueue requestQueue, int id) {
        this.requestQueue = requestQueue;
        this.id = id;
    }

    /**
     * Override run method for Thread. Waits until runnable found in request queue.
     * Runs the runnable when consumed.
     */
    @Override
    public void run() {

        while (true) {
            try {
                Runnable task = requestQueue.take();
                log.log(Level.INFO, "Request handled by thread id " + this.id);
                task.run();
            } catch (InterruptedException e) {
                throw new RuntimeException(e);
            }
        }
    }
}