#!/usr/bin/env python
# -*- coding: utf-8 -
#
# This file is part of the restpose python module, released under the MIT
# license.  See the COPYING file for more information.
"""Run the linkfinder webapp using the built-in flask webserver.

"""

from linkfinder import app
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        app.debug = True
    app.run('0.0.0.0', 5001)
