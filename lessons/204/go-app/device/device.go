package device

// The device represends a hardware unit connected to the cloud.
type Device struct {

	// The device's identifier.
	Id int `json:"id"`

	// The device's MAC address.
	Mac string `json:"mac"`

	// The device's firmware version.
	Firmware string `json:"firmware"`
}
