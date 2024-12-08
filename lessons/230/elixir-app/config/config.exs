import Config

config :app,
  ecto_repos: [App.Repo],
  generators: [timestamp_type: :utc_datetime, binary_id: true]

config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

import_config "#{config_env()}.exs"
