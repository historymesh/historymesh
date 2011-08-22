require 'active_record'

# Server where you can get chunks of the big Wikipedia dump
FILE_HOST = 'http://10.0.0.51:9292/'

# Database server articles and links
ActiveRecord::Base.establish_connection(
  :adapter  => 'postgresql',
  :host     => '10.0.0.61',
  :username => 'fort',
  :password => 'fort',
  :database => 'fort2')

root = File.dirname(__FILE__)
require root + '/models/article'
