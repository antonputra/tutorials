package main

import (
	"context"
	"fmt"
	"log"
	"net"

	pb "github.com/antonputra/tutorials/lessons/149/app/event"
	"google.golang.org/grpc"
)

var ev pb.Event

func init() {
	ev = pb.Event{
		Version:        "2.0",
		RouteKey:       "ANY /bot",
		RawPath:        "/default/bot",
		RawQueryString: "",
		Headers: &pb.Headers{
			Accept:                 "*/*",
			AcceptEncoding:         "gzip,deflate",
			ContentLength:          "129",
			ContentType:            "application/json",
			Host:                   "4o68t2fwke.execute-api.us-east-1.amazonaws.com",
			UserAgent:              "Slackbot 1.0 (+https://api.slack.com/robots)",
			XAmznTraceId:           "Root=1-60f9f121-0e6b301236f5d57d46fbd0e1",
			XForwardedFor:          "3.94.92.68",
			XForwardedPort:         "443",
			XForwardedProto:        "https",
			XSlackRequestTimestamp: "1626992929",
			XSlackSignature:        "v0=d12f7cb55add77074248241c2ec2d3c9fe4611e7879a965c92315edd8f0ec0cf",
		},
		RequestContext: &pb.RequestContext{
			AccountId:    "424432388155",
			ApiId:        "4o68t2fwke",
			DomainName:   "4o68t2fwke.execute-api.us-east-1.amazonaws.com",
			DomainPrefix: "4o68t2fwke",
			Http: &pb.Http{
				Method:    "POST",
				Path:      "/default/bot",
				Protocol:  "HTTP/1.1",
				SourcePp:  "3.94.92.68",
				UserAgent: "Slackbot 1.0 (+https://api.slack.com/robots)",
			},
			RequestId: "C5KdVjAlIAMEPzg=",
			RouteKey:  "ANY /bot",
			Stage:     "default",
			Time:      "22/Jul/2021:22:28:49 +0000",
			TimeEpoch: 1626992929961,
		},
		Body:            "{\"token\":\"UdG3UFNsPGoobvRzK5F2oIqe\",\"challenge\":\"6KaNtlamllYYaLZ7qhHxZbzyYut62TlDKu2wAZXp4rZlInRbcDTH\",\"type\":\"url_verification\"}",
		IsBase64Encoded: false,
	}
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

func (s *server) GetEvent(context.Context, *pb.Request) (*pb.Event, error) {
	return &ev, nil
}
