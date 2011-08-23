#!/usr/bin/env python

import re
import sys
import time

number_of_articles = 10173071

def main(index_file, articles_file):
    """
    :param main_file: wikipedia dump (uncompressed)
    :param index_file: index produced by parser.py

    """

    start_time = time.time()

    with open(index_file) as fh:
        with open(articles_file, "w") as fout:
            # Write out dump header
            fout.write('TRUNCATE articles CASCADE;\nCOPY articles (id, name, "offset", length) FROM stdin;\n')
            for i, line in enumerate(fh):
                # Calculate ETA
                try:
                    title, offset, length, links = line.rstrip('\n').split('\t')
                except ValueError:
                    continue
                if i % 1000 == 1:
                    time_per_page = (time.time() - start_time) / i
                    sys.stdout.write("\rProcessed %i lines: %6.2f%% - %6.2fh" % (
                        i,
                        (float(i) / number_of_articles) * 100,
                        (time_per_page * (number_of_articles - i)) / 3600.0,
                    ))
                    sys.stdout.flush()
                
                # Write out postgres row
                fout.write("%i\t%s\t%i\t%i\n" % (
                    i,
                    title.replace("\\", "\\\\"),
                    int(offset),
                    int(length),
                ))
            # Write out dump footer
            fout.write("\.\n")
            sys.stdout.write("\n")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
