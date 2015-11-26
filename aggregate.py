#!/usr/bin/env python

import time

tfmt = "%H:%M:%S"

def min_btwn(start, end):
    a = time.strptime(start, tfmt)
    b = time.strptime(end, tfmt)

    min = (b.tm_hour - a.tm_hour) * 60
    min += b.tm_min - a.tm_min
    return min

intvl_total = 0
total = 0
start = None
try:
    while True:
        s = raw_input()
        if "=>" in s:
            t = s.split()[0]
            m_count = int(s.split()[2])
            total += m_count 

            if start == None:
                start = t
                intvl_total = m_count
            else:
                if min_btwn(prev, t) > 5:
                    # last was, in fact, the end of barking
                    print start
                    print "           %s minutes" % intvl_total
                    print prev

                    start = t
                    intvl_total = m_count
                else:
                    intvl_total += m_count
        prev = s
                    

except EOFError,e:
    pass
