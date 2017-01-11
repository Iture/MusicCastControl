import MusicCastAPI
import time
import multiprocessing
import logging



class MusicCastWorker(multiprocessing.Process):

    def __init__(self,messageQ, commandQ, config):
        self.__messageQ=messageQ
        self.__commandQ=commandQ
        self.devices={}
        self.notification_port = config['mc_notification_port']
        self.last_update=0
        self.update_interval=config['mc_status_update_interval']
        multiprocessing.Process.__init__(self)
        for dev in config['mc_devices']:
            self.get_device(dev)
        return

    def run(self):

        while True:
            if time.time() > self.last_update+self.update_interval:
                self.update_devices()
                self.last_update=time.time()
            if not self.__commandQ.empty():
                while not self.__commandQ.empty():
                    task = self.__commandQ.get()
                    if task['method'] == 'command':
                        param = task['param']
                        if param == 'volume':
                            self.get_device(task['deviceId']).set_volume(task['payload'])
                        elif param == 'power':
                            self.get_device(task['deviceId']).set_power_state(task['payload'])
                        elif param == 'input':
                            self.get_device(task['deviceId']).set_input(task['payload'])
                        elif param == 'sound_program':
                            self.get_device(task['deviceId']).set_sound_program(task['payload'])
                        elif param == 'radio':
                            self.get_device(task['deviceId']).set_radio_station(task['payload'])
                        elif param == 'playback':
                            self.get_device(task['deviceId']).set_playback_status(task['payload'])
                        elif param == 'update':
                            self.get_device(task['deviceId']).get_device_status()
                            self.get_device(task['deviceId']).ensure_mode()


        return

    def get_device(self,device_id):
        if not device_id in self.devices:
            self.devices[device_id]=MusicCastAPI.MusicCastAPI(device_id, notification_port=self.notification_port)
        return self.devices[device_id]

    def update_devices(self):
        for device_id in self.devices:
            device=self.devices[device_id]
            device.get_device_status()
            device.ensure_mode()
            for param in device.status:
                self.__messageQ.put(self.prepare_message(device_id, param, device.status[param]))

        return

    def prepare_message(self, device, param_name, param_value):
        out = {
            'method': 'publish',
            'deviceId': device,
            'param': param_name,
            'payload': param_value,
            'qos': 1,
            'timestamp': time.time()
        }
        return out