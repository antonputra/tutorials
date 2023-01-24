package serializer

import (
	"encoding/json"

	pb "github.com/antonputra/tutorials/lessons/149/app/event"
	"google.golang.org/protobuf/proto"
)

// SerializeJSON serializes Event struct to bytes
func SerializeJSON(ev *pb.Event) ([]byte, error) {
	b, err := json.Marshal(ev)
	if err != nil {
		return nil, err
	}

	return b, nil
}

// SerializeProtoBuf serializes Event struct to bytes
func SerializeProtoBuf(ev *pb.Event) ([]byte, error) {
	b, err := proto.Marshal(ev)
	if err != nil {
		return nil, err
	}

	return b, nil
}

// DeserializeJSON deserializes encoded string to struct
func DeserializeJSON(b []byte) (*pb.Event, error) {
	var ev pb.Event

	err := json.Unmarshal(b, &ev)
	if err != nil {
		return &pb.Event{}, err
	}

	return &ev, nil
}

// DeserializeProtoBuf deserializes encoded protobuf to struct
func DeserializeProtoBuf(b []byte) (*pb.Event, error) {
	var ev pb.Event

	err := proto.Unmarshal(b, &ev)
	if err != nil {
		return &pb.Event{}, err
	}

	return &ev, nil
}
