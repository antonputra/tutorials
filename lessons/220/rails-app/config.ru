# This file is used by Rack-based servers to start the application.
require 'rack'
require 'prometheus/middleware/exporter'

use Prometheus::Middleware::Exporter

require_relative "config/environment"

run Rails.application
Rails.application.load_server
