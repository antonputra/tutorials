defmodule App.Telemetry do
  use Supervisor

  import Telemetry.Metrics

  def start_link(arg) do
    Supervisor.start_link(__MODULE__, arg, name: __MODULE__)
  end

  @impl true
  def init(_arg) do
    children = [{Peep, [name: :app, metrics: metrics()]}]
    Supervisor.init(children, strategy: :one_for_one)
  end

  def metrics do
    [
      distribution([:bandit, :request, :stop, :duration],
        tags: [],
        unit: {:native, :millisecond},
        reporter_options: [
          peep_bucket_calculator: App.Telemetry.Bucket
        ]
      )
    ]
  end
end
