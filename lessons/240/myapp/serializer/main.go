package serializer

import (
	"encoding/json"

	"myapp/device"

	"google.golang.org/protobuf/proto"
)

// SerializeJSON serializes Event struct to bytes
func SerializeJSON(ev *device.Device) ([]byte, error) {
	b, err := json.Marshal(ev)
	if err != nil {
		return nil, err
	}

	return b, nil
}

// SerializeProtoBuf serializes Event struct to bytes
func SerializeProtoBuf(ev *device.Device) ([]byte, error) {
	b, err := proto.Marshal(ev)
	if err != nil {
		return nil, err
	}

	return b, nil
}

// DeserializeJSON deserializes encoded string to struct
func DeserializeJSON(b []byte) (*device.Device, error) {
	var ev device.Device

	err := json.Unmarshal(b, &ev)
	if err != nil {
		return &device.Device{}, err
	}

	return &ev, nil
}

// DeserializeProtoBuf deserializes encoded protobuf to struct
func DeserializeProtoBuf(b []byte) (*device.Device, error) {
	var ev device.Device

	err := proto.Unmarshal(b, &ev)
	if err != nil {
		return &device.Device{}, err
	}

	return &ev, nil
}
