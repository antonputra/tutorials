defmodule App.Router do
  use Plug.Router

  plug(:match)
  plug(:dispatch)

  get "/metrics" do
    metrics =
      :app
      |> Peep.get_all_metrics()
      |> Peep.Prometheus.export()

    text(conn, 200, metrics)
  end

  get "/healthz" do
    text(conn, 200, "OK")
  end

  get "/api/devices" do
    devices = [
      %App.Device{
        id: 1,
        uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
        mac: "5F-33-CC-1F-43-82",
        firmware: "2.1.6",
        created_at: "2024-05-28T15:21:51.137Z",
        updated_at: "2024-05-28T15:21:51.137Z"
      },
      %App.Device{
        id: 2,
        uuid: "d2293412-36eb-46e7-9231-af7e9249fffe",
        mac: "E7-34-96-33-0C-4C",
        firmware: "1.0.3",
        created_at: "2024-01-28T15:20:51.137Z",
        updated_at: "2024-01-28T15:20:51.137Z"
      },
      %App.Device{
        id: 3,
        uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
        mac: "68-93-9B-B5-33-B9",
        firmware: "4.3.1",
        created_at: "2024-08-28T15:18:21.137Z",
        updated_at: "2024-08-28T15:18:21.137Z"
      }
    ]

    json(conn, 200, devices)
  end

  post "/api/devices" do
    try do
      {:ok, body, conn} = Plug.Conn.read_body(conn)
      body = JSON.decode!(body)
      now = DateTime.utc_now() |> DateTime.to_string()

      device =
        App.Device.save(%App.Device{
          uuid: Ecto.UUID.generate(),
          mac: body["mac"],
          firmware: body["firmware"],
          created_at: now,
          updated_at: now
        })

      json(conn, 201, device)
    rescue
      e ->
        json(conn, 400, %{message: Exception.message(e)})
    end
  end

  match _ do
    text(conn, 404, "Not found")
  end

  defp text(conn, status, body) do
    conn
    |> put_resp_content_type("text/plain")
    |> send_resp(status, body)
    |> halt()
  end

  defp json(conn, status, payload) do
    conn
    |> put_resp_content_type("application/json")
    |> send_resp(status, JSON.encode_to_iodata!(payload))
    |> halt()
  end
end
