require File.dirname(__FILE__) + '/file_server'

path = ENV['DATAFILE'] || 'README.rdoc'
run FileServer.new(path)

