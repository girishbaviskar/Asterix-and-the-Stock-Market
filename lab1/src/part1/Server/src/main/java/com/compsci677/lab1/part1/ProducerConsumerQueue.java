package com.compsci677.lab1.part1;

import java.util.LinkedList;
import java.util.Queue;

/**
 * Custom thread-safe queue following Producer-Consumer paradigm
 */
public class ProducerConsumerQueue {


    private Queue<Runnable> runnableQueue = null;

    /**
     * Constructor method for ProducerConsumerQueue. Creates a new LinkedList.
     */
    ProducerConsumerQueue() {
        this.runnableQueue = new LinkedList<Runnable>();
    }

    /**
     * Synchronized put method to add a task in the queue.
     * Provides thread safety. Holds the object monitor while adding. Releases monitor and notifies
     * an arbitrary thread when finished adding.
     *
     * @param runnable Runnable task to add in the queue
     */
    public synchronized void put(Runnable runnable) {
        try {
            runnableQueue.add(runnable);
        } catch (Exception e) {
            System.out.println(e);
        }
        notify(); // Notify an arbitrary waiting thread
    }

    /**
     * Synchronized take method to dequeue an element from the queue.
     * Awaits notification from producer thread for a non-empty queue.
     * Loops wait until runnableQueue is empty to avoid spurious wake-ups.
     *
     * @return Runnable task
     * @throws InterruptedException
     */
    public synchronized Runnable take() throws InterruptedException {
        while (runnableQueue.isEmpty()){
            wait();
        }
        Runnable task = runnableQueue.poll();
        notify(); // Notify any waiting producer
        return task;
    }
}
