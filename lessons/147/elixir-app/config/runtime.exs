import Config

config :hardware, Hardware.Endpoint, tls_enabled: System.get_env("TLS_ENABLED") in ~w(true 1)
