#!/usr/bin/env python
import time

class Stopwatch(object):
    def __init__(self):
        object.__init__(self)
        self.reset()

    def reset(self):
        self._running = False
        self._start = 0.0
        self._total = 0.0
        return self._total

    def start(self):
        if not self._running:
            self._running = True
            self._start = time.time()
            self._last = self._start
            return self._total
        else:
            return self.elapsed()

    def stop(self):
        if self._running:
            self._running = False
            now = time.time()
            self._total += now - self._start
            self._start = 0.0
        return self._total

    def elapsed(self):
        if self._running:
            now = time.time()
            return self._total + (now - self._start)
        else:
            return self._total
