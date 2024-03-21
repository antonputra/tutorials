install-protoc-gen-elixir:
	mix escript.install hex protobuf

run-protoc:
	protoc \
		--elixir_out=plugins=grpc:./lib/hardware \
		-I ./priv/proto/ \
		./priv/proto/device.proto
