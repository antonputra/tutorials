defmodule Hardware.Server do
  use GRPC.Server, service: Hardware.Manager.Service

  @message %Hardware.Device{
    uuid: "a7090a19-9f08-43ce-a3e6-7bb8641ee77d",
    mac: "EF-2B-C4-F5-D6-34",
    firmware: "2.1.6"
  }

  def get_device(_request, _stream) do
    @message
  end
end
