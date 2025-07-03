defmodule App.Device do
  @derive {JSON.Encoder, only: [:id, :uuid, :mac, :firmware, :created_at, :updated_at]}
  defstruct [:id, :uuid, :mac, :firmware, :created_at, :updated_at]

  def save(device) do
    %{uuid: uuid, mac: mac, firmware: firmware, created_at: created_at, updated_at: updated_at} =
      device

    %{rows: [[id]]} =
      App.Repo.query!(
        "INSERT INTO \"devices\" (uuid, mac, firmware, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id",
        [uuid, mac, firmware, created_at, updated_at]
      )

    %{device | id: id}
  end
end
