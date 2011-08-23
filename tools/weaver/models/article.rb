class Article < ActiveRecord::Base
  def self.search(name)
    name = name.gsub(/^(.)/) { $1.upcase }.gsub('_', ' ')
    find_by_name(name)
  end

  def html
    uri  = URI.parse("#{FILE_HOST}?offset=#{offset}&length=#{length}")
    text = Net::HTTP.get_response(uri).body

    text.force_encoding('UTF-8') if text.respond_to?(:force_encoding) # ugh
    text.gsub!(/\{\{[^\}]*\}\}/, '')

    Wikitext::Parser.new.parse(text)
  end
end
