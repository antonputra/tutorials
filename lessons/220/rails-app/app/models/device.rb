class Device < ApplicationRecord
  def save
    result = nil

    PrometheusClient.db_histogram.observe(Benchmark.realtime { result = super })

    result
  end
end
