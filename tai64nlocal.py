#!/usr/bin/python3

import pytai
import sys
import time
import re

def main():
    tairegex = re.compile(r'^(@[0-9a-f]{24})', re.IGNORECASE)
    for line in sys.stdin:
        output = ''
        # sample: @40000000470ea0e538b13329
        match = re.match(tairegex, line)
        if match:
            output = re.sub(tairegex, '', line)
            intime = match.group(1)
            tai = pytai.tai()
            tai.from_tai64n_ext(intime)
            output = str(tai) + output
        else:
            output = line
        sys.stdout.write(output)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
