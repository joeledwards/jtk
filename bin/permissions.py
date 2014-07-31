#!/usr/bin/env python
import env

from jtk.permissions import Main

if __name__ == '__main__':
    try:
        Main().start()
    except KeyboardInterrupt:
        print

