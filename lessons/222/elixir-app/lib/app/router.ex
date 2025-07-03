defmodule App.Router do
  use Plug.Router

  plug(:match)
  plug(:dispatch)

  get "/metrics" do
    metrics =
      :app
      |> Peep.get_all_metrics()
      |> Peep.Prometheus.export()

    conn
    |> put_resp_content_type("text/plain")
    |> send_resp(200, metrics)
    |> halt()
  end

  get "/healthz" do
    conn
    |> put_resp_content_type("text/plain")
    |> send_resp(200, "OK")
    |> halt()
  end

  get "/api/devices" do
    devices = [
      %{
        id: 1,
        uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
        mac: "5F-33-CC-1F-43-82",
        firmware: "2.1.6",
        created_at: "2024-05-28T15:21:51.137Z",
        updated_at: "2024-05-28T15:21:51.137Z"
      },
      %{
        id: 2,
        uuid: "d2293412-36eb-46e7-9231-af7e9249fffe",
        mac: "E7-34-96-33-0C-4C",
        firmware: "1.0.3",
        created_at: "2024-01-28T15:20:51.137Z",
        updated_at: "2024-01-28T15:20:51.137Z"
      },
      %{
        id: 3,
        uuid: "eee58ca8-ca51-47a5-ab48-163fd0e44b77",
        mac: "68-93-9B-B5-33-B9",
        firmware: "4.3.1",
        created_at: "2024-08-28T15:18:21.137Z",
        updated_at: "2024-08-28T15:18:21.137Z"
      }
    ]

    conn
    |> put_resp_content_type("application/json")
    |> send_resp(200, Jason.encode!(devices))
    |> halt()
  end

  post "/api/devices" do
    try do
      {:ok, body, conn} = Plug.Conn.read_body(conn)
      body = Jason.decode!(body)
      now = DateTime.utc_now()

      device =
        App.Repo.insert!(%App.Device{
          uuid: Ecto.UUID.generate(),
          mac: body["mac"],
          firmware: body["firmware"],
          created_at: now,
          updated_at: now
        })

      conn
      |> put_resp_content_type("application/json")
      |> send_resp(201, Jason.encode!(device))
      |> halt()
    rescue
      e ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(400, Jason.encode!(%{message: Exception.message(e)}))
        |> halt()
    end
  end

  match _ do
    conn
    |> put_resp_content_type("text/plain")
    |> send_resp(404, "Not found")
    |> halt()
  end
end
