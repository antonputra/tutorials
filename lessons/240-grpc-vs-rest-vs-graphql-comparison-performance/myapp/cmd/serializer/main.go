package main

import (
	"os"

	"myapp/device"
	"myapp/serializer"
)

var ev device.Device

func main() {
	ev = device.Device{
		Id:        1,
		Uuid:      "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
		Mac:       "EF-2B-C4-F5-D6-34",
		Firmware:  "2.1.5",
		CreatedAt: "2024-05-28T15:21:51.137Z",
		UpdatedAt: "2024-05-28T15:21:51.137Z",
	}

	Save("device")
}

// Save JSON and ProtoBuf messages to file
func Save(fname string) {
	// save JSON into file
	b, err := serializer.SerializeJSON(&ev)
	check(err)
	err = os.WriteFile(fname+".json", b, 0644)
	check(err)

	// save ProtoBuf into file
	b, err = serializer.SerializeProtoBuf(&ev)
	check(err)
	err = os.WriteFile(fname+".pb", b, 0644)
	check(err)
}

// Chek for error and panic
func check(e error) {
	if e != nil {
		panic(e)
	}
}
