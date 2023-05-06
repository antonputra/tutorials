defmodule Hardware.Device do
  @moduledoc false

  use Protobuf, protoc_gen_elixir_version: "0.12.0", syntax: :proto3

  field :uuid, 1, type: :string
  field :mac, 2, type: :string
  field :firmware, 3, type: :string
end

defmodule Hardware.DeviceRequest do
  @moduledoc false

  use Protobuf, protoc_gen_elixir_version: "0.12.0", syntax: :proto3

  field :uuid, 1, type: :string
end

defmodule Hardware.Manager.Service do
  @moduledoc false

  use GRPC.Service, name: "hardware.Manager", protoc_gen_elixir_version: "0.12.0"

  rpc :GetDevice, Hardware.DeviceRequest, Hardware.Device
end

defmodule Hardware.Manager.Stub do
  @moduledoc false

  use GRPC.Stub, service: Hardware.Manager.Service
end
