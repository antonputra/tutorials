import Config

if config_env() == :prod do
  database_url =
    System.get_env("DATABASE_URL") ||
      raise """
      environment variable DATABASE_URL is missing.
      For example: ecto://USER:PASS@HOST/DATABASE
      """

  maybe_ipv6 = if System.get_env("ECTO_IPV6") in ~w(true 1), do: [:inet6], else: []

  config :app, App.Repo,
    # ssl: true,
    url: database_url,
    pool_size: String.to_integer(System.get_env("REPO_POOL_SIZE", "10")),
    pool_count: String.to_integer(System.get_env("REPO_POOL_COUNT", "1")),
    queue_target: String.to_integer(System.get_env("REPO_QUEUE_TARGET", "50")),
    queue_interval: String.to_integer(System.get_env("REPO_QUEUE_INTERVAL", "1000")),
    socket_options: maybe_ipv6

  config :app, App.Router,
    serve: System.get_env("WEB_SERVER", "false") == "true",
    port: String.to_integer(System.get_env("WEB_PORT", "4000"))
end
