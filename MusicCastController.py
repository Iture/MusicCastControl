import json
import logging
import multiprocessing
import time

import tornado.gen
import tornado.ioloop
import tornado.websocket
from tornado.options import options

import MQTTClient
import MusicCastWorker
import EventListener

logger = logging.getLogger('MusicCast')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def main():
    # messages read from device
    messageQ = multiprocessing.Queue()
    # messages written to device
    commandQ = multiprocessing.Queue()
    config = {}
    try:
        with open('config.json') as json_data:
            config = json.load(json_data)
    except Exception as e:
        logger.error("Config load failed")
        exit(1)

    mqtt = MQTTClient.MQTTClient(messageQ, commandQ, config)
    mqtt.daemon = True
    mqtt.start()

    mw = MusicCastWorker.MusicCastWorker(messageQ, commandQ, config)
    mw.daemon = True
    mw.start()

    event_listener=EventListener.EventListener(messageQ, commandQ, config)
    event_listener.daemon = True
    event_listener.start()

    # wait a second before sending first task
    time.sleep(1)
    options.parse_command_line()

    mainLoop = tornado.ioloop.IOLoop.instance()
    mainLoop.start()


if __name__ == "__main__":
    main()
