package main

import (
	"net/http"
)

func (s *server) getDevices(w http.ResponseWriter, req *http.Request) {
	device := []Device{
		{
			Id:        1,
			Uuid:      "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
			Mac:       "EF-2B-C4-F5-D6-34",
			Firmware:  "2.1.5",
			CreatedAt: "2024-05-28T15:21:51.137Z",
			UpdatedAt: "2024-05-28T15:21:51.137Z",
		},
		{
			Id:        2,
			Uuid:      "d2293412-36eb-46e7-9231-af7e9249fffe",
			Mac:       "E7-34-96-33-0C-4C",
			Firmware:  "1.0.3",
			CreatedAt: "2024-01-28T15:20:51.137Z",
			UpdatedAt: "2024-01-28T15:20:51.137Z",
		},
		{
			Id:        3,
			Uuid:      "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
			Mac:       "68-93-9B-B5-33-B9",
			Firmware:  "4.3.1",
			CreatedAt: "2024-08-28T15:18:21.137Z",
			UpdatedAt: "2024-08-28T15:18:21.137Z",
		},
		{
			Id:        4,
			Uuid:      "ab4efcd0-f542-4944-9dd9-0ad844dfcbd3",
			Mac:       "E7-6F-69-99-F1-ED",
			Firmware:  "6.2.0",
			CreatedAt: "2024-08-29T15:18:21.137Z",
			UpdatedAt: "2024-08-29T15:18:21.137Z",
		},
		{
			Id:        5,
			Uuid:      "9e725cbc-2c4e-446c-a274-962531f90927",
			Mac:       "9F-57-E5-1F-F5-6B",
			Firmware:  "0.6.4",
			CreatedAt: "2024-18-28T15:18:21.137Z",
			UpdatedAt: "2024-18-28T15:18:21.137Z",
		},
	}

	renderJSON(w, &device, 200)
}
