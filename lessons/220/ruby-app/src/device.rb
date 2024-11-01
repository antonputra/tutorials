# frozen_string_literal: true

require 'securerandom'

require_relative 'prometheus_client'

Device = Struct.new(:id, :uuid, :mac, :firmware, :created_at, :updated_at, keyword_init: true) do
  def self.list
    [
      { 'id' => 1, 'uuid' => '9add349c-c35c-4d32-ab0f-53da1ba40a2a', 'mac' => '5F-33-CC-1F-43-82', 'firmware' => '2.1.6', 'created_at' => '2024-5-28T15:21:51.137Z', 'updated_at' => '2024-5-28T15:21:51.137Z' },
      { 'id' => 2, 'uuid' => 'd2293412-36eb-46e7-9231-af7e9249fffe', 'mac' => 'E7-34-96-33-0C-4C', 'firmware' => '1.0.3', 'created_at' => '2024-01-28T15:20:51.137Z', 'updated_at' => '2024-01-28T15:20:51.137Z' },
      { 'id' => 3, 'uuid' => 'eee58ca8-ca51-47a5-ab48-163fd0e44b77', 'mac' => '68-93-9B-B5-33-B9', 'firmware' => '4.3.1', 'created_at' => '2024-8-28T15:18:21.137Z', 'updated_at' => '2024-8-28T15:18:21.137Z' }
    ]
  end

  def self.create(params)
    now = Time.now
    uuid = SecureRandom.uuid
    device = new(uuid: uuid, mac: params['mac'], firmware: params['firmware'], created_at: now, updated_at: now)

    sql = <<~SQL
      INSERT INTO "devices" ("uuid", "mac", "firmware", "created_at", "updated_at")
      VALUES ('#{device.uuid}', '#{device.mac}', '#{device.firmware}', '#{device.created_at}', '#{device.updated_at}')
      RETURNING "id"
    SQL

    start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    PG_POOL.with do |conn|
      device.id = conn.exec(sql).first['id']
    end
    duration = Process.clock_gettime(Process::CLOCK_MONOTONIC) - start
    PrometheusClient.create_device_histogram.observe(duration, labels: { op: 'db' })

    device
  end
end
