class DevicesController < ApplicationController
  before_action :set_device, only: %i[ show update destroy ]

  # GET /devices
  def index
    devices = [
      Device.new(id: 1, uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a", mac: "5F-33-CC-1F-43-82", firmware: "2.1.6", created_at: "2024-5-28T15:21:51.137Z", updated_at: "2024-5-28T15:21:51.137Z"),
      Device.new(id: 2, uuid: "d2293412-36eb-46e7-9231-af7e9249fffe", mac: "E7-34-96-33-0C-4C", firmware: "1.0.3", created_at: "2024-01-28T15:20:51.137Z", updated_at: "2024-01-28T15:20:51.137Z"),
      Device.new(id: 3, uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77", mac: "68-93-9B-B5-33-B9", firmware: "4.3.1", created_at: "2024-8-28T15:18:21.137Z", updated_at: "2024-8-28T15:18:21.137Z")
    ]
    
    render json: devices
  end

  # GET /devices/1
  def show
    render json: @device
  end

  # POST /devices
  def create
    @device = Device.new(device_params)
    @device.uuid = SecureRandom.uuid

    if @device.save
      render json: @device, status: :created, location: @device
    else
      render json: @device.errors, status: :unprocessable_entity
    end
  end

  # PATCH/PUT /devices/1
  def update
    if @device.update(device_params)
      render json: @device
    else
      render json: @device.errors, status: :unprocessable_entity
    end
  end

  # DELETE /devices/1
  def destroy
    @device.destroy!
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_device
      @device = Device.find(params[:id])
    end

    # Only allow a list of trusted parameters through.
    def device_params
      params.require(:device).permit(:uuid, :mac, :firmware)
    end
end
