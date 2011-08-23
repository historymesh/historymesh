class Article
  attr_reader :name

  def initialize(params)
    @name = params[:name].gsub(/^(.)/) { $1.upcase }.gsub('_', ' ')
  end

  def html
    text = data['text'].gsub!(/\{\{[^\}]*\}\}/, '')
    Wikitext::Parser.new.parse(text)
  end

  def inlinks
    data['inlinks']
  end

  def outlinks
    data['outlinks']
  end

private

  def data
    return @data if defined?(@data)

    uri   = URI.parse("http://#{CONTENT_HOST}/?title=#{CGI.escape @name}")
    json  = Net::HTTP.get_response(uri).body
    @data = JSON.parse(json)
  end
end

