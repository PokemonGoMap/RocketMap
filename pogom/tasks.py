#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import schedule
import Queue
import time

from threading import Thread
from timeit import default_timer

log = logging.getLogger(__name__)

"""
Module for executing tasks, there are two types of triggers:
 * Scheduled: Tasks that should run every X minutes or at a certain time in the
   future.
 * File changes: Tasks that should run when a file is changed.

Also there are two types of tasks:
 * CPU bound: Tasks that do only processing.
 * IO bound: Tasks that do anything with network, DB or files those access can
   take more time and pass priority while waiting for IO results, to avoid
   skipping other tasks this type of tasks are executed by a thread pool.

General usage it is pretty simple for example for a task that should run every
hour to log something you could do:

def log():
    log.debug("Hello world")

t = CPUTask("logging", sched=schedule.every().hour(), target=log)

or:

LogTask(CPUTask):
    def run():
        log.debug("Hello world")
t = LogTask("logging", sched=schedule.every().hour())

For a IO bound task that runs when a file is changed it would be:

def db_query():
    pass

t = IOTask("Slow query", filename="filename.txt", target=db_query)

Subclass example is ommited for brevity.

You can mix triggers and types of tasks, just use the appropriate for every
case
"""


class BaseTask():
    """
    Base class for tasks, not intended for regular use, use instead IOTask or
    CPUTask.
    """

    def __init__(self, name, sched=None, filename=None, target=None):
        """
        Default constructor for tasks
        It will raise an Exception if both sched and filename are not defined.

        :param str name: Task name, used only for logging porpouses
        :param `sechedule.Job` sched: Period of time between task repetitions
        :param str filename: File to watch
        :param func target: Function to run if you have not inherited this to
            write your own run function
        """
        self._name = name
        self._target = target
        if not sched and not filename:
            raise Exception("No schedule or filename defined")
        if sched:
            sched.do(self._run, self)
        else:
            self._filename = filename
            self._last_modification = os.path.getmtime(filename)
            # Currently there is no reason for allow configuration of this time
            # we should change this type of trigger to use OS filesystem
            # watchers.
            schedule.every().minute().do(self._check_file(), self)

    def _check_file(self):
        """
        Internal function for checking a file and running a task if it was
        modified.
        """
        file_modified_time_sec = os.path.getmtime(self.filename)
        if self.last_modification != file_modified_time_sec:
            log.debug('Task %s: %s was changed running task', self.name,
                      self.filename)
            self.last_modification = file_modified_time_sec
            self._run()

    def run(self):
        """
        Default run function, it runs the stored _target or raises an Exception
        if no target was defined.
        """
        if self._target:
            self._target()
        else:
            raise Exception("No function was defined to run")

    def _run(self):
        """
        Internal run function added for timing and logging.
        """
        start_timer = default_timer()
        self.run()
        log.debug('Task %s run in %.6f seconds.', self.name,
                  default_timer() - start_timer)

    @staticmethod
    def _schedule_run():
        """
        Main schedule function for scheduled tasks
        """
        while True:
            schedule.run_pending()
            time.sleep(1)


class CPUTask(BaseTask):
    """
    CPUTask should be used for tasks that does not do any kind of IO, like disk
    access, network requests or DB queries, should run fast so other tasks are
    not skipped.
    """
    pass


class IOTask(BaseTask):
    """
    IOTask should be used for tasks that DOSE do any kind of IO, like disk
    access, network requests or DB queries they are run in their own thread to
    avoid skipping other tasks.
    """
    jobqueue = Queue.Queue()

    def _run(self):
        """
        Internal function that adds the run function to the queue for running.
        """
        self.jobqueue.put((self.run, self))

    @staticmethod
    def _thread_run():
        """
        Static function used by the threads in the pool for waiting for a new
        job and run it.
        It adds some logging and a warning if the queue is too big.
        """
        while True:
            (job_func, task) = IOTask.jobqueue.get()
            start_timer = default_timer()
            job_func(task)
            log.debug('Task %s run in %.6f seconds.', task.name,
                      default_timer() - start_timer)
            IOTask.jobqueue.task_done()
            size = IOTask.jobqueue.qsize()
            if size > 5:
                log.warning("Task queue is %d", size)


def init_task_scheduler(thread_count):
    """
    Main function that starts the scheduling, it does start one thread for the
    CPUTasks and a thread pool for IOTasks.
    :param int thread_count: Number of threads in the thread pool
    """
    continuous_thread = Thread(target=BaseTask._schedule_run, name='scheduler')
    continuous_thread.daemon = True
    continuous_thread.start()
    for i in range(0, thread_count):
        t = Thread(
            target=IOTask._thread_run, name='IO-worker-{}'.format(i))
        t.daemon = True
        t.start()
