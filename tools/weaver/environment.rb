require 'active_record'

# Server where you can get chunks of the big Wikipedia dump
FILE_HOST = 'http://psql.fort:9292/'

# Database server articles and links
ActiveRecord::Base.establish_connection(
  :adapter  => 'postgresql',
  :host     => 'psql.fort',
  :username => 'fort',
  :password => 'fort',
  :database => 'fort')

root = File.dirname(__FILE__)
require root + '/models/article'
