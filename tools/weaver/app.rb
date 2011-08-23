require File.expand_path('../environment', __FILE__)
require 'sinatra'

get '/' do
  Article.count.to_s
end

get '/wiki/:name.*' do
  error 404
end

get '/wiki/:name' do
  @article = Article.find(params[:name])
  @title   = @article.name
  erb :article
end

get '/faves' do
  erb :faves
end

