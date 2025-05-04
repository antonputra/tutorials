package main

type Device struct {
	Id        int    `json:"id"`
	Uuid      string `json:"uuid"`
	Mac       string `json:"mac"`
	Firmware  string `json:"firmware"`
	CreatedAt string `json:"created_at"`
	UpdatedAt string `json:"updated_at"`
}
