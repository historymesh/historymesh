#!/usr/bin/env python

import re
import sys
import time
import eventlet
from eventlet.greenpool import GreenPool
from eventlet.pools import Pool
import psycopg2
eventlet.monkey_patch()
from lxml import etree

title_regex = re.compile(r"\<title\>([^\<]+)\</title\>")
link_regex = re.compile(r"\[\[([^\]]+)\]\]")
start_pattern = '<text xml:space="preserve">'
end_pattern = '</text>'
number_of_articles = 30500000.0
max_threads = 400
max_threads_waiting = 10000


class ConnectionPool(Pool):
    def create(self):
        return psycopg2.connect(
            host = "10.0.0.61",
            user = "fort",
            database = "fort",
            password = "fort",
        )


def main(filename):

    connpool = ConnectionPool()
    with connpool.item() as connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE articles, links;")
        cursor.execute("ALTER SEQUENCE articles_id_seq RESTART 1;")
        cursor.execute("COMMIT")

    pool = GreenPool(max_threads)
    start_time = time.time()

    for i, (title, start, length, text) in enumerate(parse(filename)):
        pool.spawn(
            save_to_db,
            connpool,
            i,
            start_time,
            title,
            start,
            length,
            set(extract_links(text)),
        )
        while pool.waiting() > max_threads_waiting:
            eventlet.sleep(0.01)
            

def save_to_db(connpool, i, start_time, title, start, length, links):
    with connpool.item() as connection:
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        # Insert
        if i:
            time_per_page = (time.time() - start_time) / i
            print "%6.2f%% - %6.2fh - %s" % (
                i / number_of_articles,
                (time_per_page * (number_of_articles - i)) / 3600.0,
                title,
            )
        cursor.execute(
            'INSERT INTO articles (name, "offset", "length") VALUES (%s, %s, %s)',
            [title, start, length],
        )
        # Get the links and their IDs
        if links:
            link_params = []
            for link in links:
                link_params.extend([title, link])
            cursor.execute(
                "INSERT INTO links (\"from\", \"to\") VALUES %s" % (
                    ", ".join("(%s, %s)" for link in links)
                ),
                link_params,
            )
        cursor.execute("COMMIT")



def parse(filename):
    with open(filename, "rb") as fh:
        offset = 0
        current_title = None
        text_start = None
        text = ""
        for line in fh:
            already_added_text = False

            # See if it is a title
            title_match = title_regex.search(line)
            if title_match:
                current_title = title_match.group(1)
                text_start = None
                text = ""

            # See if it is some text
            try:
                index_of_text_start = line.index(start_pattern)
            except ValueError:
                pass
            else:
                text_start = offset + index_of_text_start + len(start_pattern)
                text += line[text_start - offset:]
                already_added_text = True
            
            # See if it's the end of some text
            try:
                index_of_text_end = line.index(end_pattern)
            except ValueError:
                pass
            else:
                text_end = offset + index_of_text_end
                text += line[:index_of_text_end]
                yield current_title, text_start, text_end - text_start, text
                text_start = None
                already_added_text = True
            
            # See if we're in the middle of a text block
            if text_start and not already_added_text:
                text += line
            
            # Increment offset
            offset += len(line)

def extract_links(text):
    # Find all potential matches
    for match in link_regex.finditer(text):
        link_text = match.group(1)
        # Discard anything with a colon that isn't "Category:"
        if ":" in link_text and not link_text.startswith("Category:"):
            continue
        # Find any pipes and cut at them
        try:
            pipe_index = link_text.index("|")
        except ValueError:
            pass
        else:
            link_text = link_text[:pipe_index]
        # Find any hashes and cut at them
        try:
            hash_index = link_text.index("#")
        except ValueError:
            pass
        else:
            link_text = link_text[:hash_index]
        # Yield the valid link
        yield link_text

if __name__ == "__main__":
    main(sys.argv[1])
