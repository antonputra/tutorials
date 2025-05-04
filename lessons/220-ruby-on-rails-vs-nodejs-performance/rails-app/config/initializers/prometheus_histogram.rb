# frozen_string_literal: true

Rails.application.config.after_initialize do
  # https://github.com/prometheus/client_ruby/pull/316

  require 'prometheus/client/metric'

  module Prometheus
    module Client
      class Histogram < Metric
        def observe(value, labels: {})
          bucket = buckets.bsearch { |upper_limit| upper_limit >= value  }
          bucket = "+Inf" if bucket.nil?

          base_label_set = label_set_for(labels)

          # This is basically faster than doing `.merge`
          bucket_label_set = base_label_set.dup
          bucket_label_set[:le] = bucket.to_s
          sum_label_set = base_label_set.dup
          sum_label_set[:le] = "sum"

          @store.synchronize do
            @store.increment(labels: bucket_label_set, by: 1)
            @store.increment(labels: sum_label_set, by: value)
          end
        end
      end
    end
  end
end
