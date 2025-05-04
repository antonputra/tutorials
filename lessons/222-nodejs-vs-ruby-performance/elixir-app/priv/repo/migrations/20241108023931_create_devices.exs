defmodule App.Repo.Migrations.CreateDevices do
  use Ecto.Migration

  def change do
    create table(:devices, primary_key: false) do
      add(:id, :bigserial, primary_key: true)
      add(:uuid, :string)
      add(:mac, :string)
      add(:firmware, :string)
      add(:created_at, :timestamptz, null: false)
      add(:updated_at, :timestamptz, null: false)
    end
  end
end
