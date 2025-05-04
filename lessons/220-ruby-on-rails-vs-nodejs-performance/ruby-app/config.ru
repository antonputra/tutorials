# frozen_string_literal: true

require 'connection_pool'
require 'oj'
require 'pg'
require 'prometheus/middleware/exporter'
require 'rack'
require 'rage'
require 'rage/fiber'
require 'rage/fiber_scheduler'
require 'rage/middleware/fiber_wrapper'
require 'yaml'

require_relative 'src/app'

RubyVM::YJIT.enable
Iodine.threads = 1
Iodine.workers = ENV.fetch('WORKERS_NUM', 2).to_i

Oj.default_options = { mode: :compat }
pg_conf = YAML.load(File.read('db/config.yml'), aliases: true)['production']
PG_POOL = ConnectionPool.new(size: pg_conf['pool'], timeout: 5) do
  PG.connect(pg_conf['host'], pg_conf['port'], nil, nil, pg_conf['database'], pg_conf['username'], pg_conf['password'])
end

# Enable if http metrics are required
# use Prometheus::Middleware::Collector
use Rage::FiberWrapper
use Prometheus::Middleware::Exporter

run App.new
