from django.core.management.base import BaseCommand, CommandError
import logging
from django.utils import timezone

import zmq
import vital.tasks as tasks
import ConfigParser

config = ConfigParser.ConfigParser()
config.optionxform=str

# TODO change to common config file in shared location
config.read("/home/vital/config.ini")

zmqMaster = config.get("VITAL", "ZMQ_MASTER")

class Command(BaseCommand):
    help = "Command to start a zmq Slave listening for tasks"

    def handle(self, *args, **options):
        zmqMaster = config.get("VITAL", "ZMQ_MASTER")
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.connect('tcp://' + zmqMaster + ':5001')

        while True:
            try:
                task_data = socket.recv_json()
                task = task_data.pop('task')
                task_kwargs = task_data.pop('task_kwargs')
                getattr(tasks, task)(**task_kwargs)
            
            except Exception, e:
                print e

        socket.close()
        context.term()
