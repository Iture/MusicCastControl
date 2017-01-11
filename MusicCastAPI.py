import requests
import socket
import select
import logging


class MusicCastAPI:
    def __init__(self, host, zone='main', notification_port=None):
        self.logger = logging.getLogger('MusicCastAPI')
        self.host = host
        self.zone = zone
        self.status = {}
        self.base_url = "http://%s/YamahaExtendedControl/v1" % self.host
        self.inputs = ['tv', 'usb', 'net_radio', 'spotify', 'hdmi', 'server', 'bluetooth']
        self.sound_programs = ['stereo', 'movie', 'music']

        self.update_features()

        self.event_port = notification_port
        self.headers = {}
        if self.event_port is not None:
            self.headers = {'X-AppName': 'MusicCast/0.001(python)', 'X-AppPort': '%s' % self.event_port}
        self.preferred_modes = {
            'tv': 'movie',
            'hdmi': 'movie',
            'net_radio': ['stereo', 'music'],
            'spotify': ['stereo', 'music'],
            'server': ['stereo', 'music'],
            'bluetooth': ['stereo', 'music'],
            'airplay': ['stereo', 'music']
        }
        self.__socket = None

    def update_features(self):
        url = "%s/system/getFeatures" % self.base_url
        self.logger.debug("Trying to update features")
        self.logger.debug("Request url: %s" % url)
        try:
            result = requests.get(url)
            if result.status_code == 200:
                r = result.json()
                self.inputs = r['zone'][0]['input_list']
                self.sound_programs = r['zone'][0]['sound_program_list']
                self.logger.debug("Features updated suceessfully")
        except Exception as ex:
            self.logger.error("Features update problem: %s" % ex)

    def get_device_status(self):
        url = "%s/%s/getStatus" % (self.base_url, self.zone)
        self.logger.debug("Trying to update status")
        self.logger.debug("Request url: %s" % url)

        try:
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200 and result.json()['response_code'] == 0:
                self.status = result.json()
        except Exception as ex:
            self.logger.error("Features update problem: %s" % ex)
        return

    def get_event(self, timeout=1):
        msg = None
        if self.__socket:
            try:
                result = select.select([self.__socket], [], [], timeout)
                if result[0]:
                    msg,addr = result[0][0].recvfrom(1024)
                    msg=str(msg)
                    self.logger.debug("Message received:%s from %s" % (msg,addr))
            except Exception as ex:
                self.logger.error("Error getting event notification: %s" % ex)
        return msg

    def ensure_mode(self):
        if self.status['input'] in self.preferred_modes \
                and self.status['sound_program'] not in self.preferred_modes[self.status['input']]:
            if type(self.preferred_modes[self.status['input']]) == list:
                pref = self.preferred_modes[self.status['input']][0]
            else:
                pref = self.preferred_modes[self.status['input']]
            self.set_sound_program(pref)
            self.logger.debug("Reset mode to :%s" % pref)

    def set_power_state(self, power_state):
        url = "%s/%s/setPower?power=%s" % (self.base_url, self.zone, power_state)
        self.logger.debug("Trying to set power mode to:%s" % power_state)
        self.logger.debug("Request url: %s" % url)

        try:
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200 and result.json()['response_code'] == 0:
                self.status['power'] = power_state
        except Exception as ex:
            self.logger.error("Problem setting power state: %s" % ex)
        return

    def set_input(self, input_name):
        if input_name in self.inputs:
            url = "%s/%s/setInput?input=%s" % (self.base_url, self.zone, input_name)
            self.logger.debug("Trying to set input to:%s" % input_name)
            self.logger.debug("Request url: %s" % url)

            try:
                result = requests.get(url)
                if result.status_code == 200 and result.json()['response_code'] == 0:
                    self.status['input'] = input_name
            except Exception as ex:
                self.logger.error("Problem setting input: %s" % ex)
        return

    def set_sound_program(self, sound_program):
        if sound_program in self.sound_programs:
            url = "%s/%s/setSoundProgram?program=%s" % (self.base_url, self.zone, sound_program)
            self.logger.debug("Trying to set sound program to:%s" % sound_program)
            self.logger.debug("Request url: %s" % url)

            try:
                result = requests.get(url)
                if result.status_code == 200 and result.json()['response_code'] == 0:
                    self.status['sound_program'] = sound_program
            except Exception as ex:
                self.logger.error("Problem setting sound program: %s" % ex)

        return

    def set_radio_station(self, preset_index):
        url = "%s/netusb/recallPreset?zone=%s&num=%s" % (self.base_url, self.zone, preset_index)
        self.logger.debug("Trying to set radio station to :%s" % preset_index)
        self.logger.debug("Request url: %s" % url)
        self.set_input('net_radio')

        try:
            result = requests.get(url)
            if result.status_code == 200 and result.json()['response_code'] == 0:
                self.logger.debug("Radio station set")
        except Exception as ex:
            self.logger.error("Problem setting radio station: %s" % ex)
        # self.set_playback_status('play')
        return

    def set_playback_status(self, status):
        playback_states = ["play", "stop", "pause", "play_pause",
                           "previous", "next", "fast_reverse_start", "fast_reverse_end",
                           "fast_forward_start", "fast_forward_end"]
        if status in playback_states:
            url = "%s/netusb/setPlayback?playback=%s" % (self.base_url, status)
            self.logger.debug("Trying to set playback status to :%s" % status)
            self.logger.debug("Request url: %s" % url)
            try:
                result = requests.get(url)
                if result.status_code == 200 and result.json()['response_code'] == 0:
                    self.logger.debug("Playback status set to: %s" % status)
            except Exception as ex:
                self.logger.error("Problem setting playback status: %s" % ex)
        return

    def set_volume(self, volume):
        url = "%s/%s/setVolume?volume=%s" % (self.base_url, self.zone, volume)
        self.logger.debug("Trying to set volume to :%s" % volume)
        self.logger.debug("Request url: %s" % url)

        try:
            result = requests.get(url)
            if result.status_code == 200 and result.json()['response_code'] == 0:
                self.status['volume'] = volume
        except Exception as ex:
            self.logger.error("Problem setting volume: %s" % ex)
        return

    def set_mute(self, state):
        url = "%s/%s/setMute?enable=%s" % (self.base_url, self.zone, state)
        self.logger.debug("Trying to set mute state to :%s" % state)
        self.logger.debug("Request url: %s" % url)

        if state in ['on', 'off']:
            try:
                result = requests.get(url)
                if result.status_code == 200 and result.json()['response_code'] == 0:
                    self.status['mute'] = state
            except Exception as ex:
                self.logger.error("Problem setting mute: %s" % ex)
        return
