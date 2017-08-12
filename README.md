# MusicCastControl
MQTT interface for Yamaha MusicCast

Receives events from the MusicCast device when a value changes and publishes them to MQTT. 

Publishes topics in the format: 

MusicCast/friendly_name/power

To set a value, use: 

MusicCast/friendly_name/power/set 

Example values from a Yamaha A2060 (Zone 3 with a friendly_name of dining_room):

MusicCast/dining_room/sleep:0
MusicCast/dining_room/input:audio3
MusicCast/dining_room/response_code:0
MusicCast/dining_room/max_volume:161
MusicCast/dining_room/distribution_enable:False
MusicCast/dining_room/power:standby
MusicCast/dining_room/volume:102
MusicCast/dining_room/enhancer:True
MusicCast/dining_room/mute:False
MusicCast/dining_room/disable_flags:0

friendly_names, ip addresses and zones are defined in config.json

To start run: 

python3 MusicCastController.py
