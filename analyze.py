#!/usr/bin/env python
import time

def dur_min(start, stop):
    a = time.strptime(start, "%H:%M:%S")
    b = time.strptime(stop, "%H:%M:%S")

    diff = 60 * (b.tm_hour - a.tm_hour)
    diff += b.tm_min - a.tm_min

    return diff

state = 0 # 0 == quiet, 1 == barking

try: 
    while True:
        s = raw_input()
        if "BE QUIET" in s:
            if state == 0:
                start = s.split()[0]
            state = 1
        elif "GOOD DOG" in s:
            if state == 1 and start != None:
                stop = s.split()[0]
                if start == None:
                    start = stop

                duration = dur_min(start, stop)
                print "%s => %s minutes" % (start, duration)
                print stop
            state = 0

except EOFError, e:
    pass


