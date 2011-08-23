require File.expand_path('../environment', __FILE__)
require 'sinatra'

get '/' do
  '<p style="font-size: 800%">In space, nobody knows you&rsquo;re a dog.</p>'
end

get '/wiki/:name.*' do
  error 404
end

get '/wiki/:name' do
  @article = Article.find(params[:name])
  @title   = @article.name
  erb :article
end

get '/stories/' do
  erb :stories
end

get '/stories/new' do
  @title = 'Create a story'
  erb :story
end

get '/stories/:name' do
  @title = params[:name]
  @story = params[:name]
  erb :story
end

get '/saved' do
  @title = 'Saved articles'
  erb :saved
end

