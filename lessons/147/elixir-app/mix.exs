defmodule MyApp.MixProject do
  use Mix.Project

  def project do
    [
      app: :hardware,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      releases: releases()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Hardware.Application, []}
    ]
  end

  defp releases do
    [hardware: [applications: [hardware: :permanent]]]
  end

  defp deps do
    [
      {:grpc, "0.5.0"},
      {:protobuf, "0.12.0"}
    ]
  end
end
