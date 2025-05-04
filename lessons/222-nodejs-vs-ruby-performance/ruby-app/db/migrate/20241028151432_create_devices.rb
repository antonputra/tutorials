# frozen_string_literal: true

class CreateDevices < ActiveRecord::Migration[7.2]
  def change
    create_table :devices do |t|
      t.string :uuid
      t.string :mac
      t.string :firmware

      t.timestamps
    end
  end
end
