#!/usr/bin/env python

import csv
import re
import restpose
import sys
import time

idesc_pattern = re.compile(r'''[_:/\\\.,\[\]{}]''')
idesc_repls = {
    '_': '__',
    ':': '_c',
    '/': '_s',
    '\\': '_b',
    '.': '_d',
    ',': '_C',
    '[': '_o',
    ']': '_e',
    '{': '_O',
    '}': '_E',
}

def idesc(id):
    return idesc_pattern.sub(lambda x: idesc_repls[x.group()], id)

number_of_articles = 10173071

def main(main_file, index_file):
    """
    :param main_file: wikipedia dump (uncompressed)
    :param index_file: index produced by parser.py

    """

    coll = restpose.Server().collection('wikilinks')
    #coll.delete()
    #coll.checkpoint().wait()
    articles = coll.doc_type('a')
    c = coll.config
    c['types']['a'] = {
        'fields': {
            '_meta': {'slot': 0, 'type': 'meta', 'group': '#'},
            'id': {'store_field': 'id', 'max_length': 30, 'type': 'id', 'too_long_action': 'hash'},
            'type': {'group': '!', 'wdfinc': 0, 'store_field': 'type', 'max_length': 64, 'too_long_action': 'error', 'type': 'exact'},
            's': {'store_field': 's', 'type': 'stored'},
            'o': {'store_field': 'o', 'type': 'stored'},
            'l': {'store_field': 'l', 'group': 'l', 'max_length': 30, 'too_long_action': 'hash', 'type': 'exact'},
            'r': {'store_field': '', 'group': 'r', 'max_length': 30, 'too_long_action': 'hash', 'type': 'exact'},
            't': {'store_field': '', 'group': 't', 'type': 'text', 'processor': 'stem_en'},
        },

        'patterns': [
            ['*', {'store_field': '*', 'group': 't', 'type': 'text'}],
        ],
    }
    coll.config = c

    start_time = time.time()

    with open(index_file) as fh:
    	for i, line in enumerate(fh):
            row = line.rstrip('\n').split('\t')
            if i % 27 == 1:
                time_per_page = (time.time() - start_time) / i
                sys.stdout.write("\rProcessed %d lines: %6.2f%% - %6.2fh" % (
                    i,
                    (float(i) / number_of_articles) * 100,
                    (time_per_page * (number_of_articles - i)) / 3600.0,
                ))

                sys.stdout.flush()
            if len(row) != 5:
                print ('\nBad row: %d' % i)
                continue
            (id, start, size, is_redirect, targets) = row
            doc = {'id': idesc(id), 's': int(start), 'o': int(size)}
            doc['t'] = id
            if is_redirect == 'true':
                doc['r'] = 'R'
            elif is_redirect == 'false':
                pass
            else:
                assert False
            links = []
            for target in targets.split('|'):
                links.append(idesc(target))
            if links:
                doc['l'] = links

            while True:
                try:
                    articles.add_doc(doc)
                    break
                except restpose.RequestFailed, e:
                    print "\nIndexing queue full ... ",
                    time.sleep(1)
                    print "retrying"

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
