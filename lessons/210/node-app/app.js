import express from "express";
import save from "./devices.js";
import summary from "./metrics.js";
import { randomUUID } from "crypto";
import { register } from "prom-client";
import config from "./config.js";

const app = express();

app.use(express.json());

// Expose Prometheus metrics.
app.get("/metrics", async (_req, res) => {
  res.setHeader("Content-Type", register.contentType);
  register.metrics().then((data) => res.status(200).send(data));
});

// Returns the status of the application.
app.get("/healthz", async (_req, res) => {
  // Placeholder for the health check
  res.send("OK");
});

// Returns a list of connected devices.
app.get("/api/devices", async (_req, res) => {
  const device = {
    uuid: "9add349c-c35c-4d32-ab0f-53da1ba40a2a",
    mac: "5F-33-CC-1F-43-82",
    firmware: "2.1.6",
  };

  res.status(200).json(device);
});

// Registers the device.
app.post("/api/devices", async (req, res) => {
  let device = req.body;

  // Generate a new UUID for the device.
  device.uuid = randomUUID();

  // Get the current time to record the duration of the request.
  const end = summary.startTimer();

  // Save the device to the database.
  save(device)
    .then(() => {
      // Record the duration of the insert query.
      end({ op: "db" });

      // Return Device back to the client.
      res.status(201).json(device);
    })
    .catch((error) => {
      // Log the error.
      console.error(error);

      // Return a summary of the error to the client.
      res.status(400).json({ message: error.message });
    });
});

app.listen(config.appPort, () => {
  console.log(`Starting the web server on port ${config.appPort}`);
});
