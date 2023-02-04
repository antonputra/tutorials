package main

import (
	"context"
	"flag"
	"log"
	"net"

	pb "github.com/antonputra/tutorials/lessons/152/app/proto"
	"google.golang.org/grpc"
)

var (
	serverAddr = flag.String("addr", "0.0.0.0:8082", "The server address in the format of host:port")
)

func main() {
	// Get command line arguments.
	flag.Parse()
	// Create a listener using the given port number.
	lis, err := net.Listen("tcp", *serverAddr)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	// Create new gRPC server/
	s := grpc.NewServer()
	// Register our listener with the gRPC server.
	pb.RegisterManagerServer(s, &server{})
	// Start the gRPC server.
	log.Fatalln(s.Serve(lis))
}

type server struct {
	pb.UnimplementedManagerServer
}

// GetMessage receives the message from the client and sends it back without any change.
func (s *server) GetMessage(ctx context.Context, msg *pb.Message) (*pb.Message, error) {
	return msg, nil
}
