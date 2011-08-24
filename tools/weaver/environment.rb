require 'json'
require 'net/http'
require 'uri'
require 'wikicloth'
require 'wikitext'

# Server to get Wikipedia article data
CONTENT_HOST = '10.0.0.66:5001'

root = File.dirname(__FILE__)
require root + '/models/article'

