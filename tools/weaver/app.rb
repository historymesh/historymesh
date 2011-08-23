require File.expand_path('../environment', __FILE__)
require 'sinatra'

get '/' do
  Article.count.to_s
end

get '/wiki/:name' do
  @article = Article.new(params)
  @title   = @article.name
  erb :article
end

get '/faves' do
  erb :faves
end

