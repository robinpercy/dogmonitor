#!/usr/bin/python

"""
The goal of this script is to provide positive-reinforcement for dogs when they're 
left alone.  It will monitor the average volume in a room and assumes that any noise 
above a specific threshold is barking.

When barking starts, it plays a wav file that corrects the dogs.  After a brief 
period of silence, it plays a wav file that encourages the dogs.  Ultimately, the 
logic for both of these will involve exponential back-offs.

TODO:
    * Add an exponential back off to the "good dog" wav file
    * Start communicating the "correct" and "encourage" events to an arduino 
        (so we can release treats as part of encouragement)
    * Monitor external factors that may correlate and predict barking so we can 
        pre-empt it with positive feedback.  Potential variables could be: average 
        volume in room (indicating noise from outside), time of day, temperature in room.
"""
import select
import pyaudio
import wave
import sys
import time
from array import array

DEBUG = False
CHUNK = 8192
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
WAVE_OUTPUT_FILENAME = "output.wav"
QUIET_FILENAME = "quiet.wav"
GOOD_DOG1_FILENAME = "good_dogs1.wav"
GOOD_DOG2_FILENAME = "good_dogs2.wav"

MIN_RESPONSE_INTERVAL_SECS = 10 
MAX_RESPONSE_INTERVAL_SECS = 30 
RESPONSE_DELAY_RATE = 1.6 

THRESHOLD = 7500

if sys.platform == 'darwin':
    CHANNELS = 1


"""
Initialize the two wave files we'll use for correction and encouragement
"""
quiet_wav = wave.open(QUIET_FILENAME)  
good_dog_wavs = [wave.open(GOOD_DOG1_FILENAME), wave.open(GOOD_DOG2_FILENAME)]

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
wav_variation = 1
response_data = ""
frames = array('h')
dogs_were_quiet = True
dogs_are_barking = False
seconds_until_reward = MIN_RESPONSE_INTERVAL_SECS

def avg_volume(stream):
    global CHUNK, THRESHOLD
    data = array('h',stream.read(CHUNK))
    return sum([abs(i) for i in data]) / len(data)

def check_for_barking(volume):
    return volume > THRESHOLD 

def respond_to_current_activity(dogs_were_quiet, dogs_are_barking, seconds_quiet):
    global wf,response_data, seconds_until_reward, wav_variation

    if dogs_were_quiet and dogs_are_barking: 
#        wf = quiet_wav
#        wf.rewind()
#        response_data = wf.readframes(CHUNK)
        print "%s BE QUIET!" % time.strftime("%H:%M:%S")

    elif seconds_quiet > seconds_until_reward:
        wav_variation = (wav_variation + 1) % len(good_dog_wavs) 
        wf = good_dog_wavs[wav_variation]
        wf.rewind()
        response_data = wf.readframes(CHUNK)
        print "%s GOOD DOG! %s/%s" % (time.strftime("%H:%M:%S"), seconds_quiet, seconds_until_reward)
        seconds_until_reward += MAX_RESPONSE_INTERVAL_SECS

def log_noise_level(volume, seconds_quiet):
    if DEBUG:
        sys.stdout.write("                                         ")
        sys.stdout.write("\rVolume: %s : %s " % (volume, seconds_quiet))
        sys.stdout.flush()


"""
Loop until the user hits Ctrl+C. 
In the loop, we analyze the latest buffer from pyaudio then decide whether or not
to initiate playing a wav file.

When playing a wav file, we only write out one CHUNK of buffer per iteration.
Otherwise, pyaudio complains of a buffer overflow when we try to read from 
the input buffer. So, this means the loop is either in one of three states:
    1. Not Playing Wave File
    2. Playing "Good Dog" Wave File
    3. Playing "Be Quiet" Wave file

The states are determined by the wf and response_data variables.  If response_data contains 
data, then a file is being played and wf will be pointed at the file being played.  
Note that we're careful not to initiate playing a file if one is already being played.
"""
try: 
    while True:
        volume = avg_volume(stream)
        dogs_are_barking = check_for_barking(volume)
        seconds_quiet = time.time() - last_noise

        log_noise_level(volume, seconds_quiet);

        if dogs_are_barking:
            last_noise = time.time()
            seconds_until_reward = MIN_RESPONSE_INTERVAL_SECS


        """
        If we don't have output queued up, check if we should start playing one 
        of the wav files
        """
        if response_data == "":
            respond_to_current_activity(dogs_were_quiet, dogs_are_barking, seconds_quiet)

        """
        If we have output queued up, play the next chunk of it
        """
        if response_data != "":
            stream.write(response_data)
            response_data = wf.readframes(CHUNK)

        dogs_were_quiet = not dogs_are_barking

        
except (KeyboardInterrupt):
    print("Exiting")

stream.stop_stream()
stream.close()
p.terminate()

