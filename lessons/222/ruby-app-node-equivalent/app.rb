# frozen_string_literal: true

require 'rack'
require 'webrick'
require 'webrick/httpservlet'
require 'stringio'
require 'json'
require 'securerandom'
require 'prometheus/client'
require 'prometheus/client/formats/text'
require_relative 'config'
require_relative 'metrics'
require_relative 'devices'

# Timeout in milliseconds (60 seconds)
class App
  def call(env)
    req = Rack::Request.new(env)

    case req.path
    when '/'
      [200, { 'Content-Type' => 'text/plain' }, ['Hello, World!']]
    when '/metrics'
      registry = Prometheus::Client.registry
      metrics_text = Prometheus::Client::Formats::Text.marshal(registry)
      [200, { 'Content-Type' => 'text/plain; version=0.0.4; charset=utf-8' }, [metrics_text]]

    when '/healthz'
      [200, { 'Content-Type' => 'text/plain' }, ['OK']]

    when '/api/devices'
      if req.get?
        devices = [
          {
            id: 1,
            uuid: '9add349c-c35c-4d32-ab0f-53da1ba40a2a',
            mac: '5F-33-CC-1F-43-82',
            firmware: '2.1.6',
            created_at: '2024-05-28T15:21:51.137Z',
            updated_at: '2024-05-28T15:21:51.137Z'
          },
          {
            id: 2,
            uuid: 'd2293412-36eb-46e7-9231-af7e9249fffe',
            mac: 'E7-34-96-33-0C-4C',
            firmware: '1.0.3',
            created_at: '2024-01-28T15:20:51.137Z',
            updated_at: '2024-01-28T15:20:51.137Z'
          },
          {
            id: 3,
            uuid: 'eee58ca8-ca51-47a5-ab48-163fd0e44b77',
            mac: '68-93-9B-B5-33-B9',
            firmware: '4.3.1',
            created_at: '2024-08-28T15:18:21.137Z',
            updated_at: '2024-08-28T15:18:21.137Z'
          }
        ]

        [200, { 'Content-Type' => 'application/json' }, [JSON.generate(devices)]]
      elsif req.post?
        body = req.body.read
        device = JSON.parse(body)

        datetime = Time.now.utc.iso8601(3)

        device['uuid'] = SecureRandom.uuid
        device['created_at'] = datetime
        device['updated_at'] = datetime

        start_time = Time.now
        begin
          record = save_device(
            uuid: device['uuid'],
            mac: device['mac'],
            firmware: device['firmware'],
            created_at: device['created_at'],
            updated_at: device['updated_at']
          )
          duration = Time.now - start_time
          HISTOGRAM.observe({ op: 'db' }, duration)

          device['id'] = record[0]['id'].to_i

          [201, { 'Content-Type' => 'application/json' }, [JSON.generate(device)]]
        rescue StandardError => e
          puts e.message
          puts e.backtrace.join("\n")

          [400, { 'Content-Type' => 'application/json' }, [JSON.generate({ message: e.message })]]
        end
      else
        [404, { 'Content-Type' => 'text/plain' }, ['Not Found']]
      end

    else
      [404, { 'Content-Type' => 'text/plain' }, ['Not Found']]
    end
  end
end

app = App.new

# Create a Rack adapter for WEBrick
class RackAdapter < WEBrick::HTTPServlet::AbstractServlet
  def initialize(server, app)
    super(server)
    @app = app
  end

  def service(req, res)
    body_content = req.body || ''
    input = StringIO.new(body_content)
    input.set_encoding(Encoding::BINARY)

    env = {
      'REQUEST_METHOD' => req.request_method,
      'SCRIPT_NAME' => '',
      'PATH_INFO' => req.path,
      'QUERY_STRING' => req.query_string || '',
      'SERVER_NAME' => req.host,
      'SERVER_PORT' => req.port.to_s,
      'rack.version' => Rack::VERSION,
      'rack.url_scheme' => (req.request_uri.scheme rescue 'http'),
      'rack.input' => input,
      'rack.errors' => $stderr,
      'rack.multithread' => false,
      'rack.multiprocess' => false,
      'rack.run_once' => false,
      'CONTENT_LENGTH' => body_content.bytesize.to_s,
      'CONTENT_TYPE' => req.content_type || ''
    }

    req.header.each do |key, values|
      env["HTTP_#{key.upcase.tr('-', '_')}"] = values.join(', ')
    end

    status, headers, body = @app.call(env)

    res.status = status
    headers.each { |key, value| res[key] = value }
    body.each { |chunk| res.body << chunk.to_s }
  end
end

server = WEBrick::HTTPServer.new(
  BindAddress: '0.0.0.0',
  Port: CONFIG['appPort']
)

server.mount('/', RackAdapter, app)

puts "Ruby is listening on http://0.0.0.0:#{CONFIG['appPort']} ..."

trap('INT') { server.shutdown }
server.start

