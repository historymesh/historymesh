#!/usr/bin/env python
# -*- coding: utf-8 -
#
# This file is part of the restpose python module, released under the MIT
# license.  See the COPYING file for more information.
"""Simple webapp for browsing contents of a restpose server.

"""

from flask import Flask, make_response, request
import restpose
import json
import re

idesc_pattern = re.compile(r'''[_:/\\\.,\[\]{}]''')
idunesc_pattern = re.compile(r'''_.''')
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
idunesc_repls = dict((v, k) for (k, v) in idesc_repls.iteritems())

def idesc(id):
    return idesc_pattern.sub(lambda x: idesc_repls[x.group()], id)
def idunesc(id):
    return idunesc_pattern.sub(lambda x: idunesc_repls[x.group()], id)

app = Flask(__name__)
server = restpose.Server()
docs = server.collection('wikilinks').doc_type('a')
main_file = 'enwiki-latest-pages-articles.xml'

@app.route('/')
def frontpage():
    args = request.args
    title = idesc(args.get('title'))
    try:
        doc = docs.field('id').equals(title)[0]
    except IndexError:
        return 'null'

    inlinks = [idunesc(d.data['id'][0]) for d in docs.field('l').equals(title)[:10000]]
    size = doc.data['o'][0]
    start = doc.data['s'][0]
    with open(main_file) as fh:
        fh.seek(start)
        text = fh.read(size)

    result = {
        'title': doc.data['id'][0],
        'outlinks': map(idunesc, doc.data['l']),
        'inlinks': inlinks,
        'text': text
    }
    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/search')
def search():
    args = request.args
    title = args.get('title')
    results = docs.field('t').text(title)[:1000]

    result = dict(
        articles = [idunesc(r.data['id'][0]) for r in results],
    )

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response
