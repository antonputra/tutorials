defmodule Hardware.Endpoint do
  use GRPC.Endpoint
  run(Hardware.Server)

  def child_spec(_opts) do
    GRPC.Server.Supervisor.child_spec(__MODULE__, 50050, tls_option([]))
  end

  defp tls_option(opts) do
    case tls_enabled?() do
      false ->
        opts

      true ->
        Keyword.put(
          opts,
          :cred,
          GRPC.Credential.new(ssl: [certfile: "cert.pem", keyfile: "key.pem"])
        )
    end
  end

  defp tls_enabled? do
    :hardware
    |> Application.get_env(__MODULE__, [])
    |> Keyword.get(:tls_enabled, false)
  end
end
