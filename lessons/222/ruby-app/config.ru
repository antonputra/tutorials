# frozen_string_literal: true

require 'connection_pool'
require 'iodine'
require 'oj'
require 'pg'
require 'prometheus/middleware/exporter'
require 'rack'
require 'yaml'

require_relative 'src/app'

RubyVM::YJIT.enable
Iodine.threads = ENV.fetch('RAILS_MAX_THREADS', 2).to_i
Iodine.workers = ENV.fetch('WORKERS_NUM', 2).to_i
Oj.default_options = { mode: :compat }
pg_conf = YAML.load(File.read('db/config.yml'), aliases: true)['production']
PG_POOL = ConnectionPool.new(size: Iodine.threads * Iodine.workers, timeout: 5) do
  PG.connect(pg_conf['host'], pg_conf['port'], nil, nil, pg_conf['database'], pg_conf['username'], pg_conf['password'])
end

# Enable if http metrics are required
# use Prometheus::Middleware::Collector
use Prometheus::Middleware::Exporter

run App.new
