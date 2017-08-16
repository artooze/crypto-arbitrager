import logging
import json
import time
import os
import math
import os, time
import sys
import traceback

class Push:
    def __init__(self, zmq_port, zmq_host=None):
        self.zmq_port = zmq_port
        self.zmq_host = zmq_host
        self.is_terminated = False

    def terminate(self):
        self.is_terminated = True

    def process_message(self,message):
        pass

    def msg_server(self):
        import zmq
        import time
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://*:%s"%self.zmq_port)

        logging.info("zmq msg_server start...")
        while not self.is_terminated:
            # Wait for next request from client
            message = socket.recv()
            logging.info("new pull message: %s", message)
            self.process_message(message)

            time.sleep (1) # Do some 'work'

    def notify_obj(self, pyObj):
        import zmq
        try:
            context = zmq.Context()
            socket = context.socket(zmq.PUSH)

            socket.connect ("tcp://%s:%s" % (self.zmq_host, self.zmq_port))

            message = json.dumps(pyObj)
            logging.info( "notify message %s", message)

            socket.send_string(message)
        except Exception as e:
            logging.warn("notify_msg Exception", exc_info=True)
            pass

    def notify_msg(self, type, price):
        message = {'type':type, 'price':price}
        self.notify_obj(message)