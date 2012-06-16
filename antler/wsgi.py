import os
from os.path import abspath, dirname, join
import site
import sys

project_name = 'antler'

prev_sys_path = list(sys.path)

relative_paths = ['..', '.', 'apps/', '%s_ve/lib/python2.7/site-packages' % project_name]

for relative_path in relative_paths:
    site.addsitedir(abspath(join(dirname(__file__), relative_path)))

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

os.environ["DJANGO_SETTINGS_MODULE"] = "%s.configs.production.settings" % project_name

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()
