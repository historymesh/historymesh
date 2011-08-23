require 'cgi'
require 'json'
require 'net/http'
require 'uri'
require 'wikicloth'

# Server to get Wikipedia article data
CONTENT_HOST = '10.0.0.53:5001'

root = File.dirname(__FILE__)
require root + '/models/article'

