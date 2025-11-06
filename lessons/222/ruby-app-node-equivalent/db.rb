# frozen_string_literal: true

require 'pg'
require_relative 'config'

# Creates a connection pool to connect to Postgres.
# Connection is established lazily to avoid errors on startup if DB is not available
module DB
  def self.connection
    @connection ||= PG.connect(
      host: CONFIG['db']['host'],
      dbname: CONFIG['db']['database'],
      user: CONFIG['db']['user'],
      password: CONFIG['db']['password'],
      port: 5432
    )
  end

  def self.exec_params(*args)
    connection.exec_params(*args)
  end
end

