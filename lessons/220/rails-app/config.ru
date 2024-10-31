# This file is used by Rack-based servers to start the application.
require 'rack'
require 'prometheus/middleware/collector'
require 'prometheus/middleware/exporter'

use Rack::Deflater
use Prometheus::Middleware::Collector
use Prometheus::Middleware::Exporter

run ->(_) { [200, {'content-type' => 'text/html'}, ['OK']] }

require_relative "config/environment"

run Rails.application
Rails.application.load_server
