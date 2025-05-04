package main

// Device represents hardware device
type Device struct {

	// Device identifier
	Id int `json:"id"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}
