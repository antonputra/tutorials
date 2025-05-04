require "test_helper"

class DevicesControllerTest < ActionDispatch::IntegrationTest
  setup do
    @device = devices(:one)
  end

  test "should get index" do
    get devices_url, as: :json
    assert_response :success
  end

  test "should create device" do
    assert_difference("Device.count") do
      post devices_url, params: { device: { firmware: @device.firmware, mac: @device.mac, uuid: @device.uuid } }, as: :json
    end

    assert_response :created
  end

  test "should show device" do
    get device_url(@device), as: :json
    assert_response :success
  end

  test "should update device" do
    patch device_url(@device), params: { device: { firmware: @device.firmware, mac: @device.mac, uuid: @device.uuid } }, as: :json
    assert_response :success
  end

  test "should destroy device" do
    assert_difference("Device.count", -1) do
      delete device_url(@device), as: :json
    end

    assert_response :no_content
  end
end
