class FileServer
  def initialize(path)
    @path = File.expand_path(path)
  end

  def call(env)
    request = Rack::Request.new(env)
    offset  = request.params['offset'].to_i
    length  = request.params['length'].to_i


    text = ""
    File.open(@path, 'r') do |file|
      file.seek(offset)
      text = file.read(length) || ''
    end

    text.force_encoding('UTF-8') if text.respond_to?(:force_encoding)

    [200, {'Content-Type' => 'text/plain'}, [text]]
  end
end

