# frozen_string_literal: true

require_relative 'db'

# Inserts a Device into the Postgres database.
def save_device(uuid:, mac:, firmware:, created_at:, updated_at:)
  result = DB.exec_params(
    'INSERT INTO "node_device" ("uuid", "mac", "firmware", "created_at", "updated_at") VALUES ($1, $2, $3, $4, $5) RETURNING "id"',
    [uuid, mac, firmware, created_at, updated_at]
  )
  result
end

