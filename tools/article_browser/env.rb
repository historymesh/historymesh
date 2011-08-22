require 'active_record'

ActiveRecord::Base.establish_connection(
  :adapter  => 'postgresql',
  :host     => '10.0.0.61',
  :username => 'fort',
  :password => 'fort',
  :database => 'fort2')

root = File.dirname(__FILE__)
require root + '/model/article'

