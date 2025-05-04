package main

// Device represents hardware device
type Device struct {

	// Universally unique identifier
	UUID string `json:"uuid"`

	// Mac address
	Mac string `json:"mac"`

	// Firmware version
	Firmware string `json:"firmware"`
}
