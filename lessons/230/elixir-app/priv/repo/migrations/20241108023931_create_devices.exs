defmodule App.Repo.Migrations.CreateDevices do
  use Ecto.Migration

  def change do
    create table(:devices) do
      add(:uuid, :string)
      add(:mac, :string)
      add(:firmware, :string)
      add(:created_at, :string, null: false)
      add(:updated_at, :string, null: false)
    end
  end
end
