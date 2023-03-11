package main

import (
	"context"
	"fmt"
	"log"
	"net"

	pb "github.com/antonputra/tutorials/lessons/143/myapp/device"
	"google.golang.org/grpc"
)

var dv pb.Device

func init() {
	dv = pb.Device{Uuid: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"}
}

func main() {
	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", 8082))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterManagerServer(s, &server{})
	s.Serve(lis)
}

type server struct {
	pb.UnimplementedManagerServer
}

func (s *server) GetDevice(context.Context, *pb.DeviceRequest) (*pb.Device, error) {
	return &dv, nil
}
