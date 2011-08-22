require File.dirname(__FILE__) + '/file_server'

path = 'README.rdoc'
run FileServer.new(path)

