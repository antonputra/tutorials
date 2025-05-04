package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"strconv"

	pb "github.com/antonputra/tutorials/lessons/147/go-app/proto"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

var dv pb.Device

func init() {
	dv = pb.Device{Uuid: "b0e42fe7-31a5-4894-a441-007e5256afea", Mac: "5F-33-CC-1F-43-82", Firmware: "2.1.6"}
}

func main() {
	tlsEnabled, err := strconv.ParseBool(os.Getenv("TLS_ENABLED"))
	if err != nil {
		log.Fatalf("failed to strconv.ParseBool: %v", err)
	}

	lis, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", 50050))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	var s *grpc.Server
	if tlsEnabled {
		fmt.Println("Starting gRPC server WITH TLS...")
		creds, err := credentials.NewServerTLSFromFile("cert.pem", "key.pem")
		if err != nil {
			log.Fatalf("Failed to setup TLS: %v", err)
		}
		s = grpc.NewServer(grpc.Creds(creds))
	} else {
		fmt.Println("Starting gRPC server WITHOUT TLS...")
		s = grpc.NewServer()
	}
	pb.RegisterManagerServer(s, &server{})
	s.Serve(lis)
}

type server struct {
	pb.UnimplementedManagerServer
}

func (s *server) GetDevice(context.Context, *pb.DeviceRequest) (*pb.Device, error) {
	return &dv, nil
}
