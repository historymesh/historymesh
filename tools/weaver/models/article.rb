class Article
  attr_reader :name

  def self.find(name)
    @cache ||= {}
    @cache[name] ||= new(name)
  end

  def initialize(name)
    @name = name.gsub(/^(.)/) { $1.upcase }.gsub('_', ' ')
  end

  def html
    return @html if defined?(@html)
    text = data['text'].gsub(/\{\{[^\}]*\}\}/, '')
    @html = WikiCloth::Parser.new(:data => text).to_html
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
puts uri
    json  = Net::HTTP.get_response(uri).body
puts json
    @data = JSON.parse(json)
  end
end

