defmodule App.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [App.Telemetry, App.Repo] ++ web_server()
    opts = [strategy: :one_for_one, name: App.Supervisor]
    Supervisor.start_link(children, opts)
  end

  defp web_server do
    cfg = Application.get_env(:app, App.Router, [])

    case cfg[:serve] do
      true ->
        [{Bandit, plug: App.Router, port: cfg[:port]}]

      _ ->
        []
    end
  end
end
