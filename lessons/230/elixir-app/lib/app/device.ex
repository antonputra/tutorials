defmodule App.Device do
  defstruct  [:id, :uuid, :mac, :firmware, :created_at, :updated_at]

  def save({uuid, mac, firmware, created_at, updated_at} = _device) do
    %{rows: [[id]]} =
      App.Repo.query!(
        "INSERT INTO devices (uuid, mac, firmware, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id",
        [uuid, mac, firmware, created_at, updated_at]
      )

    {id, uuid, mac, firmware, created_at, updated_at}
  end

  def to_map({id, uuid, mac, firmware, created_at, updated_at}) do
    %{
      id: id,
      uuid: uuid,
      mac: mac,
      firmware: firmware,
      created_at: created_at,
      updated_at: updated_at
    }
  end
end
