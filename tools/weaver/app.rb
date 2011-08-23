require File.expand_path('../environment', __FILE__)
require 'sinatra'
require 'cgi'
require 'net/http'
require 'uri'
require 'wikitext'

get '/' do
  Article.count.to_s
end

get '/wiki/:name' do
  @article = Article.search(params[:name])
  @title   = @article.name
  erb :article
end

get '/faves' do
  erb :faves
end
