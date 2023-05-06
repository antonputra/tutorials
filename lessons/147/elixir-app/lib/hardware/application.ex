defmodule Hardware.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [Hardware.Endpoint]
    opts = [strategy: :one_for_one, name: Hardware.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
