defmodule App.Device do
  use Ecto.Schema

  @derive {Jason.Encoder, only: [:id, :uuid, :mac, :firmware, :created_at, :updated_at]}
  schema "devices" do
    field(:uuid, :string)
    field(:mac, :string)
    field(:firmware, :string)
    field(:created_at, :utc_datetime_usec)
    field(:updated_at, :utc_datetime_usec)
  end
end
