#!/usr/bin/env falcon-host

load :rack

hostname = File.basename(__dir__)
port = ENV['PORT'] || 8080

service hostname do
  include Falcon::Environment::Rack

  append preload('preload.rb')
  count ENV.fetch('WEB_CONCURRENCY', Etc.nprocessors).to_i
  endpoint Async::HTTP::Endpoint.parse("http://0.0.0.0:#{port}")
end
