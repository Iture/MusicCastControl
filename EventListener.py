import logging
import multiprocessing
import select
import socket
import time


class EventListener (multiprocessing.Process):
    def __init__(self,messageQ, commandQ, config):
        multiprocessing.Process.__init__(self)
        self.logger = logging.getLogger('MusicCast.EventListener')
        self.logger.info("Starting...")
        self.__commandQ=commandQ
        self.logger.debug("Opening listening socket")
        self.event_port=config['mc_notification_port']
        try:
            self.__socket = socket.socket(socket.AF_INET,  # Internet
                                          socket.SOCK_DGRAM)  # UDP
            self.__socket.bind(('', self.event_port))
            self.__socket.setblocking(0)
        except Exception as ex:
            self.logger.error("Problem opening event socket:%s" % ex)

    def run(self):
        while True:
            addr, message = self.get_event(1)
            if message and 'main' in str(message):
                data_out = {
                    'method': 'command',
                    'topic': message,
                    'deviceId': addr[0],
                    'param': 'update',
                    'payload': 0,
                    'qos': 1,
                    'timestamp': time.time()
                }
                self.logger.debug("update message:%s" % data_out)
                self.__commandQ.put(data_out)


    def get_event(self, timeout=1):
        msg = None
        if self.__socket:
            addr=None
            try:
                result = select.select([self.__socket], [], [], timeout)
                if result[0]:
                    msg, addr = result[0][0].recvfrom(1024)
                    msg = str(msg)
                    self.logger.debug("Message received:%s from %s" % (msg, addr))
            except Exception as ex:
                self.logger.error("Error getting event notification: %s" % ex)
        return (addr,msg)