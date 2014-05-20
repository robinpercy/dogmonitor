#!/usr/bin/python
"""
PyAudio example: Record a few seconds of audio and save to a WAVE
file.
"""

import pyaudio
import wave
import sys
import time
from array import array


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5 
WAVE_OUTPUT_FILENAME = "output.wav"
QUIET_FILENAME = "quiet.wav"
GOOD_DOG_FILENAME = "good_dogs.wav"
PLAYING = False

last_noise = time.time()

if sys.platform == 'darwin':
    CHANNELS = 1

p = pyaudio.PyAudio()

input_stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

quiet_wav = wave.open(QUIET_FILENAME)  
good_dog_wav = wave.open(GOOD_DOG_FILENAME)

data_out = ""

frames = array('h')

"""
def say(wav, CHUNK):

    wav.rewind()
    return quiet_wav.readframes(CHUNK)
    """

QUIET = False
NOISY = True
sound_was = QUIET
sound_is = QUIET
i = 0;
try: 
    while True:
        sound_was = sound_is 
        data = array('h',input_stream.read(CHUNK))
        avg = sum([abs(i) for i in data]) / len(data)
        sound_is = avg > 500 
        sys.stdout.write("                                         ")
        if sound_is == NOISY:
            last_noise = time.time()

        quiet_since = time.time() - last_noise
        notice = ""
        if sound_was == NOISY and sound_is == QUIET and data_out == "": 
            notice = "All is calm" 
            wf = quiet_wav
            wf.rewind()
            data_out = wf.readframes(CHUNK)
        elif data_out == "" and quiet_since > 3.0:
            wf = good_dog_wav
            wf.rewind()
            data_out = wf.readframes(CHUNK)
            #data_out = say(good_dog_wav, CHUNK)


        if data_out != "":
            input_stream.write(data_out)
            data_out = wf.readframes(CHUNK)

        sys.stdout.write("\rNoise level: %s : %s " % (avg, quiet_since))
        sys.stdout.flush()
        #frames.extend(data)
        
except (KeyboardInterrupt):
    print("Exiting")


input_stream.stop_stream()
input_stream.close()
p.terminate()

"""
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
"""
