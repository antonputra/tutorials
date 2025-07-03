# frozen_string_literal: true

class DevicesController < ApplicationController
  # GET /devices
  def index
    devices = [
      Device.new(id: 1, uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a", mac: "5F-33-CC-1F-43-82", firmware: "2.1.6", created_at: "2024-5-28T15:21:51.137Z", updated_at: "2024-5-28T15:21:51.137Z").attributes,
      Device.new(id: 2, uuid: "d2293412-36eb-46e7-9231-af7e9249fffe", mac: "E7-34-96-33-0C-4C", firmware: "1.0.3", created_at: "2024-01-28T15:20:51.137Z", updated_at: "2024-01-28T15:20:51.137Z").attributes,
      Device.new(id: 3, uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77", mac: "68-93-9B-B5-33-B9", firmware: "4.3.1", created_at: "2024-8-28T15:18:21.137Z", updated_at: "2024-8-28T15:18:21.137Z").attributes
    ]

    build_response(devices, 200)
  end

  # POST /devices
  def create
    device = Device.new(params.slice(:mac, :firmware))
    device.uuid = SecureRandom.uuid

    if device.save
      build_response(device, 201)
    else
      build_response(device.errors, 422)
    end
  end

  private

  def build_response(body, status_code)
    self.content_type = "application/json"
    self.status = status_code
    self.response_body = body.to_json
  end
end
