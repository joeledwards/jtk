#!/usr/bin/env python
import time

shortest_sleep = 100000
longest_sleep = 0.0
total_sleep = 0.0
iterations = 10000
last = time.time()
for i in xrange(0, iterations):
    time.sleep(0.000001)
    now = time.time()
    duration = now - last
    total_sleep += duration
    if (duration < shortest_sleep):
        shortest_sleep = duration
    if (duration > longest_sleep):
        longest_sleep = duration
    last = now

average_sleep = total_sleep / iterations
print "average sleep duration is %0.6f seconds" % average_sleep
print "shortest sleep duration was %0.6f seconds" % shortest_sleep
print "longest sleep duration was %0.6f seconds" % longest_sleep
