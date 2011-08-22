require File.expand_path('../env', __FILE__)
require 'sinatra'
require 'net/http'
require 'uri'
require 'nokogiri'
require 'wikitext'

FILE_HOST = 'http://localhost:8000/'

get '/' do
  Article.count.to_s
end

get '/articles/:id' do
  article = Article.find(params[:id])
  uri     = URI.parse("#{FILE_HOST}?offset=#{article.offset}&length=#{article.length}")
  xml     = Net::HTTP.get_response(uri).body
  text    = Nokogiri::XML(xml).search('text').first.text
  html    = Wikitext::Parser.parse(text)

  html
end

