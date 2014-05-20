#!/usr/bin/python

"""
The goal of this script is to provide positive-reinforcement for dogs when they're left alone.  It will monitor the average volume in a room and assumes that any noise above a specific threshold is barking.

When barking starts, it plays a wav file that corrects the dogs.  After a brief period of silence, it plays a wav file that encourages the dogs.  Ultimately, the logic for both of these will involve exponential back-offs.

TODO:
    * Add an exponential back off to the "good dog" wav file
    * Start communicating the "correct" and "encourage" events to an arduino (so we can release treats as part of encouragement)
    * Monitor external factors that may correlate and predict barking so we can pre-empt it with positive feedback.  Potential variables could be: average volume in room (indicating noise from outside), time of day, temperature in room.
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
QUIET = False
NOISY = True
THRESHOLD = 500

if sys.platform == 'darwin':
    CHANNELS = 1


"""
Initialize the two wave files we'll use for correction and encouragement
"""
quiet_wav = wave.open(QUIET_FILENAME)  
good_dog_wav = wave.open(GOOD_DOG_FILENAME)

"""
Setup a full duplex stream using default devices
"""
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

last_noise = time.time()
data_out = ""
frames = array('h')
sound_was = QUIET
sound_is = QUIET

def avg_volume(stream):
    global CHUNK, THRESHOLD
    data = array('h',stream.read(CHUNK))
    return sum([abs(i) for i in data]) / len(data)

def is_noisy(volume):
    return volume > THRESHOLD

"""
Loop until the user hits Ctrl+C. In the loop, we analyze the latest buffer from pyaudio then decide whether or not
to initiate playing a wav file.

When playing a wav file, we only write out one CHUNK of buffer per iteration.  Otherwise, pyaudio complains of a buffer overflow when we try to read from the input buffer. So, this means the loop is either in one of three states:
    1. Not Playing Wave File
    2. Playing "Good Dog" Wave File
    3. Playing "Be Quiet" Wave file

The states are determined by the wf and data_out variables.  If data_out contains data, then a file is being played and wf will be pointed at the file being played.  Note that we're careful not to initiate playing a file if one is already being played.
"""
try: 
    while True:
        sound_was = sound_is 
        volume = avg_volume(stream)
        sound_is = is_noisy(volume)

        if sound_is == NOISY:
            last_noise = time.time()

        seconds_quiet = time.time() - last_noise

        """
        If we don't have output queued up, check if we should start playing one of the wav files
        """
        if data_out == "":
            if sound_was == QUIET and sound_is == NOISY: 
                wf = quiet_wav
                wf.rewind()
                data_out = wf.readframes(CHUNK)
            elif seconds_quiet > 3.0:
                wf = good_dog_wav
                wf.rewind()
                data_out = wf.readframes(CHUNK)

        """
        If we have output queued up, play the next chunk of it
        """
        if data_out != "":
            stream.write(data_out)
            data_out = wf.readframes(CHUNK)

        sys.stdout.write("                                         ")
        sys.stdout.write("\rVolume: %s : %s " % (volume, seconds_quiet))
        sys.stdout.flush()
        
except (KeyboardInterrupt):
    print("Exiting")


stream.stop_stream()
stream.close()
p.terminate()

