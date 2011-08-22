#!/usr/bin/env python

import sys

def main(main_file, index_file, title):

    # First, scan through the index file looking for the line
    print >>sys.stderr, "Scanning index file..."
    with open(index_file) as fh:
        for i, line in enumerate(fh):
            if i % 1000000 == 0 and i:
                print >>sys.stderr, "%s lines" % i
            if line.startswith(title + "\t"):
                title, offset, length, links = line.split("\t", 3)
                break

    print >>sys.stderr, "Offset %s, length %s" % (offset, length)

    # Next, read the main file
    print >>sys.stderr, "Extracting from main file..."
    with open(main_file) as fh:
        fh.seek(int(offset))
        print fh.read(int(length))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], " ".join(sys.argv[3:]))
