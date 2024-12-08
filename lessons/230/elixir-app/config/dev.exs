import Config

config :app, App.Repo,
  username: "elixir",
  password: "devops123",
  hostname: "postgres.antonputra.pvt",
  database: "mydb",
  stacktrace: true,
  show_sensitive_data_on_connection_error: true,
  pool_size: 20

config :logger, :console, format: "[$level] $message\n"

config :app, App.Router, serve: true, port: 4000
