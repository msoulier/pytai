#!/usr/bin/env python

import pytai
import sys
import time

def main():
    while True:
        for line in sys.stdin.xreadlines():
            now = pytai.now()
            print "%s %s" % (now.to_tai64n_ext(), line),
        sys.stdout.flush()
        time.sleep(1)
        if not sys.stdin.closed:
            sys.stdin.seek(0, 1)
        else:
            break

if __name__ == '__main__':
    main()
